import sqlite3
from sqlite3 import Error

# Define the name of our database file
DATABASE_FILE = "medicinal_plants.db"

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to database: {db_file}")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table created successfully.")
    except Error as e:
        print(e)

def main():
    # SQL statements for creating each table
    # We use "IF NOT EXISTS" to prevent errors if we run the script multiple times

    # 1. Species Table
    sql_create_species_table = """
    CREATE TABLE IF NOT EXISTS Species (
        species_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scientific_name TEXT NOT NULL UNIQUE,
        english_name TEXT,
        local_name TEXT,
        kingdom TEXT
    );
    """

    # 2. MedicinalUses Table
    sql_create_medicinal_uses_table = """
    CREATE TABLE IF NOT EXISTS MedicinalUses (
        use_id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL,
        part_used TEXT,
        usage_description TEXT NOT NULL,
        source_db TEXT,
        FOREIGN KEY (species_id) REFERENCES Species (species_id)
    );
    """

    # 3. Observations Table
    sql_create_observations_table = """
    CREATE TABLE IF NOT EXISTS Observations (
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        data_source TEXT NOT NULL,
        timestamp TEXT,
        health_condition TEXT,
        image_url TEXT,
        is_verified BOOLEAN DEFAULT 0,
        FOREIGN KEY (species_id) REFERENCES Species (species_id)
    );
    """

    # 4. InvasiveStatus Table
    sql_create_invasive_status_table = """
    CREATE TABLE IF NOT EXISTS InvasiveStatus (
        status_id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL,
        is_invasive BOOLEAN NOT NULL DEFAULT 0,
        source_db TEXT,
        FOREIGN KEY (species_id) REFERENCES Species (species_id)
    );
    """

    # Create database connection
    conn = create_connection(DATABASE_FILE)

    # Create tables
    if conn is not None:
        create_table(conn, sql_create_species_table)
        create_table(conn, sql_create_medicinal_uses_table)
        create_table(conn, sql_create_observations_table)
        create_table(conn, sql_create_invasive_status_table)
        
        # Close the connection
        conn.close()
        print("Database and tables created successfully. Connection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()