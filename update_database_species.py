import sqlite3

DATABASE_FILE = "medicinal_plants.db"

# The 12 classes from your 7GB dataset
new_plants_data = [
    ("Mangifera indica", "Mango", "Aam"),
    ("Terminalia arjuna", "Arjun", "Arjun"),
    ("Alstonia scholaris", "Alstonia Scholaris", "Devil Tree"),
    ("Psidium guajava", "Guava", "Amrood"),
    ("Aegle marmelos", "Bael", "Bael"),
    ("Syzygium cumini", "Jamun", "Jamun"),
    ("Jatropha curcas", "Jatropha", "Jatropha"),
    ("Millettia pinnata", "Pongamia Pinnata", "Karanj"),
    ("Ocimum tenuiflorum", "Holy Basil", "Tulsi"), # This is a duplicate, will be skipped
    ("Punica granatum", "Pomegranate", "Anaar"),
    ("Citrus limon", "Lemon", "Neembu"),
    ("Platanus orientalis", "Chinar", "Chinar")
]

print(f"Connecting to {DATABASE_FILE}...")
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

plants_added = 0
for plant in new_plants_data:
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
        # This will happen for "Ocimum tenuiflorum" since we added it already
        print(f"Skipping duplicate: {scientific_name}")
    except Exception as e:
        print(f"Error inserting {scientific_name}: {e}")

# Save (commit) changes and close
conn.commit()
conn.close()

print("\n--- Process Complete ---")
print(f"Successfully added {plants_added} new plant species.")