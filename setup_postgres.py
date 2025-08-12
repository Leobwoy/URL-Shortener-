import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    """Create the PostgreSQL database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="mynewpassword",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'url_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'url_db'...")
            cursor.execute("CREATE DATABASE url_db")
            print("Database 'url_db' created successfully!")
        else:
            print("Database 'url_db' already exists.")
        
        cursor.close()
        conn.close()
        
        print("PostgreSQL setup completed!")
        
    except Exception as e:
        print(f"Error setting up PostgreSQL: {e}")
        print("Please make sure PostgreSQL is running and the credentials are correct.")

if __name__ == "__main__":
    setup_database()
