import sqlite3
import requests
import time

DATABASE_FILE = "medicinal_plants.db"

# The list of 15 plants we want to find map data for.
# We use the exact names from our database.
PLANT_NAMES = [
    "Acacia dealbata Link",
    "Acacia mearnsii De Wild.",
    "Acacia melanoxylon R.Br.",
    "Acalypha ciliata Forssk.",
    "Acanthospermum hispidum DC.",
    "Acmella radicans (Jacquin) R.K.Jansen",
    "Aerva javanica Juss.", # Using the name from the DB
    "Aeschynomene americana L.",
    "Ageratina adenophora (Spreng.) R.M.King & H.Rob.",
    "Ageratina riparia (Regel) R.M.King & H.Rob.",
    "Azadirachta indica",
    "Ocimum tenuiflorum",
    "Curcuma longa",
    "Withania somnifera",
    "Tinospora cordifolia"
    # --- New 11 ---
    "Mangifera indica",
    "Terminalia arjuna",
    "Alstonia scholaris",
    "Psidium guajava",
    "Aegle marmelos",
    "Syzygium cumini",
    "Jatropha curcas",
    "Millettia pinnata",
    "Punica granatum",
    "Citrus limon",
    "Platanus orientalis"
]

# GBIF API settings
GBIF_API_URL = "https://api.gbif.org/v1/occurrence/search"
INDIA_COUNTRY_CODE = "IN" # We only want results from India

def get_species_id(cursor, scientific_name):
    """Finds the database ID for a given plant name."""
    try:
        cursor.execute("SELECT species_id FROM Species WHERE scientific_name = ?", (scientific_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        print(f"Error finding ID for {scientific_name}: {e}")
    return None

def fetch_gbif_locations(scientific_name):
    """Fetches up to 100 map coordinates for a species from GBIF."""
    params = {
        'scientificName': scientific_name,
        'country': INDIA_COUNTRY_CODE,
        'hasCoordinate': 'true', # Only get records that have lat/lon
        'limit': 100 # Get 100 pins per plant (to keep this fast)
    }
    
    try:
        response = requests.get(GBIF_API_URL, params=params, timeout=30)
        response.raise_for_status() # Raise an error for bad responses
        data = response.json()
        
        locations = []
        if 'results' in data:
            for record in data['results']:
                if 'decimalLatitude' in record and 'decimalLongitude' in record:
                    locations.append({
                        'lat': record['decimalLatitude'],
                        'lon': record['decimalLongitude'],
                        'date': record.get('eventDate', 'unknown')
                    })
        return locations
        
    except requests.exceptions.RequestException as e:
        print(f"  [GBIF Error] Could not fetch data for {scientific_name}: {e}")
        return []

def main():
    print(f"Connecting to {DATABASE_FILE}...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    total_locations_added = 0
    
    for plant_name in PLANT_NAMES:
        print(f"\n--- Processing: {plant_name} ---")
        
        # 1. Get the plant's ID from our database
        species_id = get_species_id(cursor, plant_name)
        
        if not species_id:
            print(f"  Could not find {plant_name} in database. Skipping.")
            continue
            
        # 2. Fetch location data from GBIF
        print(f"  Fetching locations from GBIF...")
        locations = fetch_gbif_locations(plant_name)
        
        if not locations:
            print("  No locations found on GBIF.")
            continue
            
        print(f"  Found {len(locations)} locations. Inserting into database...")
        
        # 3. Insert locations into our 'Observations' table
        locations_added_for_this_plant = 0
        for loc in locations:
            try:
                cursor.execute(
                    """INSERT INTO Observations 
                       (species_id, latitude, longitude, data_source, timestamp, is_verified) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (species_id, loc['lat'], loc['lon'], 'GBIF', loc['date'], True)
                )
                locations_added_for_this_plant += 1
            except sqlite3.IntegrityError:
                pass # Skip duplicates
            except Exception as e:
                print(f"    Error inserting location: {e}")
        
        print(f"  Successfully added {locations_added_for_this_plant} new locations.")
        total_locations_added += locations_added_for_this_plant
        
        # Be polite to the API - wait 1 second before the next request
        time.sleep(1) 

    # Save (commit) all changes and close
    conn.commit()
    conn.close()

    print("\n--- Map Data Loading Complete ---")
    print(f"Successfully added a total of {total_locations_added} map coordinates to the database.")

if __name__ == '__main__':
    main()