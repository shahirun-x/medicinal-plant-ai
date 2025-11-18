import sqlite3
import csv
import os

DATABASE_FILE = "medicinal_plants.db"
TAXON_FILE = "taxon.txt"
PROFILE_FILE = "speciesprofile.txt"

def main():
    # --- Part 1: Read the data files into memory ---
    
    # We use a dictionary to store data from speciesprofile.txt
    # We will use the species 'id' as the key.
    species_profiles = {}

    print(f"Reading {PROFILE_FILE}...")
    try:
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            # csv.reader helps us read tab-separated files
            reader = csv.reader(f, delimiter='\t')
            header = next(reader) # Skip the header row
            
            # Find the column numbers we need
            id_col = header.index('id')
            invasive_col = header.index('isInvasive')
            
            for row in reader:
                species_id = row[id_col]
                invasive_status = row[invasive_col]
                
                # We only care about species that are explicitly 'Invasive'
                if invasive_status == 'Invasive':
                    species_profiles[species_id] = {
                        'is_invasive': True
                    }

    except FileNotFoundError:
        print(f"ERROR: Cannot find {PROFILE_FILE}. Make sure it's in the same folder.")
        return
    except Exception as e:
        print(f"Error reading {PROFILE_FILE}: {e}")
        return

    print(f"Found {len(species_profiles)} invasive species in the profile file.")

    # --- Part 2: Connect to the database and insert data ---
    
    print(f"Connecting to database {DATABASE_FILE}...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    print(f"Reading {TAXON_FILE} and inserting into database...")
    
    plants_added = 0
    try:
        with open(TAXON_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader) # Skip the header
            
            id_col = header.index('id')
            name_col = header.index('scientificName')
            kingdom_col = header.index('kingdom')

            for row in reader:
                species_id = row[id_col]
                
                # Check if this ID is in our 'invasive' list
                if species_id in species_profiles:
                    kingdom = row[kingdom_col]
                    
                    # We only want to add PLANTS
                    if kingdom == 'Plantae':
                        scientific_name = row[name_col]
                        
                        try:
                            # Step A: Insert into the 'Species' table
                            cursor.execute(
                                "INSERT INTO Species (scientific_name, kingdom) VALUES (?, ?)",
                                (scientific_name, 'Plantae')
                            )
                            
                            # Get the 'species_id' that the database just created
                            new_species_id = cursor.lastrowid
                            
                            # Step B: Insert into the 'InvasiveStatus' table
                            cursor.execute(
                                "INSERT INTO InvasiveStatus (species_id, is_invasive, source_db) VALUES (?, ?, ?)",
                                (new_species_id, True, 'GRIIS-India')
                            )
                            
                            plants_added += 1

                        except sqlite3.IntegrityError:
                            # This happens if the 'scientific_name' is already in the database
                            print(f"Skipping duplicate: {scientific_name}")
                        except Exception as e:
                            print(f"Error inserting {scientific_name}: {e}")

    except FileNotFoundError:
        print(f"ERROR: Cannot find {TAXON_FILE}. Make sure it's in the same folder.")
        conn.close()
        return
    except Exception as e:
        print(f"Error reading {TAXON_FILE}: {e}")
        conn.close()
        return

    # --- Part 3: Save (commit) changes and close ---
    conn.commit()
    conn.close()
    
    print("\n--- Process Complete ---")
    print(f"Successfully added {plants_added} invasive plant species to the database.")

if __name__ == '__main__':
    main()