import sqlite3

DATABASE_FILE = "medicinal_plants.db"

# Our list of new native plants to add
native_plants = [
    ("Azadirachta indica", "Neem", "Vembu"),
    ("Ocimum tenuiflorum", "Holy Basil", "Tulsi"),
    ("Curcuma longa", "Turmeric", "Manjal"),
    ("Withania somnifera", "Ashwagandha", "Ashwagandha"),
    ("Tinospora cordifolia", "Guduchi", "Amruthavalli")
]

print(f"Connecting to {DATABASE_FILE}...")
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

plants_added = 0
for plant in native_plants:
    scientific_name, english_name, local_name = plant
    try:
        # Insert into the 'Species' table
        cursor.execute(
            "INSERT INTO Species (scientific_name, english_name, local_name, kingdom) VALUES (?, ?, ?, ?)",
            (scientific_name, english_name, local_name, 'Plantae')
        )
        plants_added += 1
        print(f"Added: {scientific_name}")
        
    except sqlite3.IntegrityError:
        print(f"Skipping duplicate: {scientific_name}")
    except Exception as e:
        print(f"Error inserting {scientific_name}: {e}")

# Save (commit) changes and close
conn.commit()
conn.close()

print("\n--- Process Complete ---")
print(f"Successfully added {plants_added} new native plant species.")