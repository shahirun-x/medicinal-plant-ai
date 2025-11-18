import sqlite3

DATABASE_FILE = "medicinal_plants.db"

# The new columns we want to add to the 'Species' table
new_columns = {
    'plant_description': 'TEXT',
    'habitat_type': 'TEXT',
    'flowering_season': 'TEXT',
    'general_warnings': 'TEXT'
}

def main():
    print(f"Connecting to {DATABASE_FILE} to upgrade table...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    columns_added = 0
    
    for column_name, data_type in new_columns.items():
        try:
            # We use "ALTER TABLE" to add a new column
            # This is safer than remaking the whole table
            cursor.execute(f"ALTER TABLE Species ADD COLUMN {column_name} {data_type}")
            print(f"Successfully added column: {column_name}")
            columns_added += 1
        except sqlite3.OperationalError as e:
            # This error happens if the column already exists, which is fine
            if "duplicate column name" in str(e):
                print(f"Column '{column_name}' already exists. Skipping.")
            else:
                print(f"An error occurred with {column_name}: {e}")
        except Exception as e:
            print(f"A general error occurred: {e}")

    # Save (commit) changes and close
    conn.commit()
    conn.close()
    
    print("\n--- Database Upgrade Complete ---")
    if columns_added > 0:
        print(f"Successfully added {columns_added} new columns to the 'Species' table.")
    else:
        print("All new columns were already present.")

if __name__ == '__main__':
    main()