import sqlite3

DATABASE_FILE = "medicinal_plants.db"

# Medicinal data for the 12 plants from the classification dataset
new_medicinal_data = [
    ("Mangifera indica", "Leaf, Bark, Fruit", "Leaves used for diabetes. Bark as an astringent for dysentery. Fruit is a rich source of vitamins."),
    ("Terminalia arjuna", "Bark", "Bark decoction is a famous cardiac tonic. Used to treat high blood pressure and other heart ailments."),
    ("Alstonia scholaris", "Bark, Leaves", "Bark (Saptaparni) is used to treat fever, malaria, skin diseases, and diarrhea."),
    ("Psidium guajava", "Leaves, Fruit", "Leaf decoction is widely used to treat diarrhea, dysentery, and as an antiseptic gargle for mouth ulcers."),
    ("Aegle marmelos", "Fruit, Leaves", "Unripe fruit is used for dysentery and diarrhea. Ripe fruit is a laxative. Leaf decoction used for fevers."),
    ("Syzygium cumini", "Seeds, Fruit, Bark", "Seeds are famously used to control diabetes. Fruit is used for digestive ailments. Bark is astringent."),
    ("Jatropha curcas", "Latex (sap), Oil, Leaves", "Latex is applied to wounds and stings to stop bleeding. Oil is a powerful purgative (use with caution). Leaves are used for rashes."),
    ("Millettia pinnata", "Oil, Leaves", "Oil (Karanja oil) is a powerful antiseptic and is widely used for skin diseases like eczema and scabies. Twigs used for dental health."),
    ("Punica granatum", "Fruit Rind, Bark, Seeds", "Fruit rind is a strong astringent, used to treat dysentery and diarrhea. Bark is used to expel tapeworms. Seed oil is rich in antioxidants."),
    ("Citrus limon", "Fruit", "Rich in Vitamin C, used to prevent scurvy. Juice is a flavoring agent, a digestive, and used in remedies for colds and fevers."),
    ("Platanus orientalis", "Bark, Leaves", "Bark and leaves are used as an antiseptic and astringent. A decoction is used for dysentery, skin infections, and to stop bleeding.")
]

def main():
    print(f"Connecting to {DATABASE_FILE}...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    uses_added = 0
    uses_skipped = 0
    
    for item in new_medicinal_data:
        scientific_name, part_used, usage_description = item
        
        try:
            # 1. Find the species_id
            cursor.execute("SELECT species_id FROM Species WHERE scientific_name = ?", (scientific_name,))
            result = cursor.fetchone()
            
            if result:
                species_id = result[0]
                
                # 2. Insert the medicinal use
                cursor.execute(
                    "INSERT INTO MedicinalUses (species_id, part_used, usage_description, source_db) VALUES (?, ?, ?, ?)",
                    (species_id, part_used, usage_description, 'Manual Research (Batch 2)')
                )
                uses_added += 1
                print(f"Added use for: {scientific_name}")
            else:
                print(f"Could not find species: {scientific_name}. Skipping.")
                uses_skipped += 1
                
        except sqlite3.IntegrityError:
            print(f"Use already exists for: {scientific_name}. Skipping.")
            uses_skipped += 1
        except Exception as e:
            print(f"Error inserting use for {scientific_name}: {e}")
            uses_skipped += 1

    conn.commit()
    conn.close()

    print("\n--- Process Complete ---")
    print(f"Successfully added {uses_added} new medicinal uses.")
    print(f"Skipped {uses_skipped} entries.")

if __name__ == '__main__':
    main()