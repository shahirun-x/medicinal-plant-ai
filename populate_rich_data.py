import sqlite3
import requests
import wikipediaapi
import time
import os

DATABASE_FILE = "medicinal_plants.db"
TREFLE_API_URL = "https://trefle.io/api/v6/species"

# --- 1. Setup APIs ---

# Trefle (Botany Data)
TREFLE_TOKEN = input("Please paste your Trefle.io API key: ")
if not TREFLE_TOKEN:
    print("API key is required. Exiting.")
    exit()

# Wikipedia (General Description)
wiki_api = wikipediaapi.Wikipedia(
    'MedicinalPlantProject/1.0 (shahirun@example.com)', 
    'en'
)

def get_db_connection():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- 2. API Helper Functions ---

def fetch_wikipedia_data(plant_name):
    """Gets a short summary and warning (if any) from Wikipedia."""
    try:
        page = wiki_api.page(plant_name)
        if not page.exists():
            return None, None # No page found

        summary = page.summary
        
        warnings = None
        if "Toxicity" in page.sections:
            warnings = page.section_by_title("Toxicity").text
        elif "Adverse effects" in page.sections:
            warnings = page.section_by_title("Adverse effects").text

        description = ". ".join(summary.split(".")[:3]) + "."
        
        return description, warnings
        
    except Exception as e:
        print(f"  [Wiki Error] {e}")
        return None, None

def fetch_trefle_data(plant_name):
    """Gets habitat and flowering data from Trefle."""
    
    # --- THIS IS THE FIX ---
    # Clean the plant name to only be Genus + Species
    # e.g., "Opuntia elatior Mill." becomes "Opuntia elatior"
    name_parts = plant_name.split()
    simple_name = " ".join(name_parts[:2])
    # --- END OF FIX ---

    params = {
        'token': TREFLE_TOKEN,
        'q': simple_name  # Use the simple name for the query
    }
    
    try:
        response = requests.get(f"{TREFLE_API_URL}/search", params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get('data'):
            print(f"  [Trefle Info] No results found for '{simple_name}'")
            return None, None # Plant not found in Trefle

        # Get the first result's ID
        species_id = search_data['data'][0]['id']
        
        # Now, get the full species details
        details_response = requests.get(f"{TREFLE_API_URL}/{species_id}", params={'token': TREFLE_TOKEN})
        details_response.raise_for_status()
        plant = details_response.json().get('data', {})

        # Extract the data we want
        habitat = plant.get('growth', {}).get('habitat', None)
        flowering = plant.get('flower', {}).get('conspicuous_period_en', None)
        
        print(f"  [Trefle Info] Found data for '{simple_name}'")
        return habitat, flowering

    except Exception as e:
        print(f"  [Trefle Error] {e}")
        return None, None

# --- 3. Main Database Population Script ---

def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all plants that we haven't processed yet
    cursor.execute("SELECT species_id, scientific_name FROM Species WHERE plant_description IS NULL")
    plants_to_process = cursor.fetchall()

    if not plants_to_process:
        print("All plants are already populated with rich data.")
        conn.close()
        return

    print(f"Found {len(plants_to_process)} plants to update...")

    for plant in plants_to_process:
        species_id = plant['species_id']
        name = plant['scientific_name']
        print(f"\n--- Processing: {name} (ID: {species_id}) ---")
        
        # 1. Fetch data from Wikipedia
        print("  Querying Wikipedia...")
        description, warnings = fetch_wikipedia_data(name)
        
        # 2. Fetch data from Trefle
        print("  Querying Trefle.io...")
        habitat, flowering = fetch_trefle_data(name)

        # 3. Update the database
        try:
            cursor.execute(
                """
                UPDATE Species 
                SET 
                    plant_description = ?, 
                    habitat_type = ?, 
                    flowering_season = ?,
                    general_warnings = ?
                WHERE 
                    species_id = ?
                """,
                (description, habitat, flowering, warnings, species_id)
            )
            print("  ...Success! Database updated.")
            
        except Exception as e:
            print(f"  [DB Error] Failed to update: {e}")

        # Commit (save) after each plant
        conn.commit()
        # Be polite to the APIs, wait a second
        time.sleep(1) 

    conn.close()
    print("\n--- Rich Data Population Complete ---")

if __name__ == "__main__":
    main()