import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    """Create the PostgreSQL database if it doesn't exist."""
    try:
        # Get database configuration from environment variables
        host = os.environ.get('DB_HOST', 'localhost')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', '')
        port = os.environ.get('DB_PORT', '5432')
        database = os.environ.get('DB_NAME', 'url_db')
        
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{database}'...")
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"Database '{database}' created successfully!")
        else:
            print(f"Database '{database}' already exists.")
        
        cursor.close()
        conn.close()
        
        print("PostgreSQL setup completed!")
        
    except Exception as e:
        print(f"Error setting up PostgreSQL: {e}")
        print("Please make sure PostgreSQL is running and the credentials are correct.")

if __name__ == "__main__":
    setup_database()
