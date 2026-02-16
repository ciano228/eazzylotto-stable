import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Crée une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'katooling_main_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_session_id(session_name):
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM work_sessions WHERE name = %s", (session_name,))
            row = cur.fetchone()
            if row:
                print(row[0])
            else:
                print(f"Session '{session_name}' not found.")
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    get_session_id('test session')
