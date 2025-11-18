import sqlite3

DATABASE_FILE = "medicinal_plants.db"

print(f"Connecting to {DATABASE_FILE}...")
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

print("Fetching first 10 invasive plants from the database...")

# This query joins the two tables to get the names and status
query = """
SELECT 
    Species.scientific_name, 
    InvasiveStatus.source_db
FROM 
    Species
JOIN 
    InvasiveStatus ON Species.species_id = InvasiveStatus.species_id
WHERE 
    InvasiveStatus.is_invasive = 1
LIMIT 10;
"""

try:
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print("\n--- Data Verification Successful! ---")
        for i, row in enumerate(results):
            print(f"  Plant {i+1}: {row[0]} (Source: {row[1]})")
    else:
        print("No data found. The database might be empty.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    conn.close()
    print("\nDatabase connection closed.")