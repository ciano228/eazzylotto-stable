import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def get_postgres_connection():
    """Connexion à PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def test_connection():
    """Test de connexion"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        conn.close()
        return True, version[0]
    except Exception as e:
        return False, str(e)