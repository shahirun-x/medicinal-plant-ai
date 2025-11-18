import sqlite3

DATABASE_FILE = "medicinal_plants.db"

# This is the data we collected, formatted for our script.
# (scientific_name, part_used, usage_description)
medicinal_data = [
    # Invasive Species
    ("Acacia dealbata Link", "Flowers, Gum, Bark", "Flower extracts have antioxidant and antimicrobial properties. Gum is edible. Bark contains tannin."),
    ("Acacia mearnsii De Wild.", "Bark, Leaves", "Bark is tannin-rich; used as an astringent for diarrhea, dysentery, and stomachaches. Bark infusion used for indigestion."),
    ("Acacia melanoxylon R.Br.", "Bark, Leaves", "Bark is soaked in water and used as an analgesic (pain relief) to bathe painful joints. Also used for anti-arthritic activity."),
    ("Acalypha ciliata Forssk.", "Leaves, Root", "Leaf paste is applied to eczema, ringworm, and minor cuts. Root infusion taken for schistosomiasis. Leaf decoction used for female sterility."),
    ("Acanthospermum hispidum DC.", "Leaves, Herb", "Crushed herb is used as a paste for skin ailments. Leaf juice is used to relieve fevers. Also used for asthma, bronchitis, and as an anthelmintic (parasite clearance)."),
    ("Acmella radicans (Jacquin) R.K.Jansen", "Flower heads, Leaves", "Known as the 'toothache plant'. Chewing fresh flower heads or leaves produces a numbing (local anesthetic) effect to relieve toothaches and gum infections."),
    ("Aerva javanica (Burm. f.) Juss.", "Whole plant, Roots, Flowers", "Used to treat kidney stones ('Pashanbheda' - stone breaker). Roots and flowers used for rheumatism. Leaf decoction used as a gargle for gum swelling and toothache."),
    ("Aeschynomene americana L.", "Root, Aerial parts", "(Uses based on related A. aspera) Used to treat mumps, cold, cough, fever, and painful micturition. Also shows analgesic and antidiarrheal activities."),
    ("Ageratina adenophora (Spreng.) R.M.King & H.Rob.", "Leaves", "Used in traditional medicine to treat wounds, itching, measles, and skin diseases. Has antibacterial, analgesic (pain relief), and antipyretic (fever-reducing) properties."),
    ("Ageratina riparia (Regel) R.M.King & H.Rob.", "Leaves, Flowers", "Used to treat wounds and stop bleeding (hemostatic). Herbal tea from leaves/flowers used to reduce blood pressure and blood sugar. Also used for skin infections and fever."),
    
    # Native Species
    ("Azadirachta indica", "Leaves, Bark, Oil, Twigs", "General antiseptic. Used for skin diseases (eczema, ringworm, psoriasis). Twigs used as 'toothbrushes' for dental health. Oil used for head lice. Leaf extract helps lower blood sugar."),
    ("Ocimum tenuiflorum", "Leaves, Seeds", "Adaptogen for stress. Leaf tea is a common remedy for colds, coughs, fever, and respiratory disorders. Used as an oral disinfectant for mouth ulcers. Also used for kidney stones."),
    ("Curcuma longa", "Rhizome (root)", "Powerful anti-inflammatory and antioxidant (curcumin). Used for digestive issues, osteoarthritis, hay fever, depression, and liver protection. Also a strong antimicrobial."),
    ("Withania somnifera", "Root, Leaves", "Powerful adaptogen for stress, anxiety, and insomnia. Used as an anti-inflammatory for rheumatism. Enhances brain function, memory, and boosts the immune system."),
    ("Tinospora cordifolia", "Stem, Root, Leaves", "Powerful immunomodulator to boost the immune system. Used to treat fevers (including dengue), colds, diabetes (regulates blood sugar), jaundice, and rheumatoid arthritis.")
]

def main():
    print(f"Connecting to {DATABASE_FILE}...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    uses_added = 0
    uses_skipped = 0
    
    for item in medicinal_data:
        scientific_name, part_used, usage_description = item
        
        try:
            # Step 1: Find the species_id for this plant
            cursor.execute("SELECT species_id FROM Species WHERE scientific_name = ?", (scientific_name,))
            result = cursor.fetchone()
            
            if result:
                species_id = result[0]
                
                # Step 2: Insert the medicinal use into the MedicinalUses table
                cursor.execute(
                    "INSERT INTO MedicinalUses (species_id, part_used, usage_description, source_db) VALUES (?, ?, ?, ?)",
                    (species_id, part_used, usage_description, 'Manual Research')
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

    # Save (commit) changes and close
    conn.commit()
    conn.close()

    print("\n--- Process Complete ---")
    print(f"Successfully added {uses_added} new medicinal uses.")
    print(f"Skipped {uses_skipped} entries (either duplicates or species not found).")

if __name__ == '__main__':
    main()