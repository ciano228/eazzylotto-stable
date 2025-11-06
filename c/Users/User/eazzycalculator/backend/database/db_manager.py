"""
Configuration centrale pour la gestion des bases de données EazzyCalculator
"""
import os
from pathlib import Path
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import DictCursor
import sqlite3
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class DatabaseConfig:
    """Classe de configuration des bases de données"""
    
    def __init__(self):
        # Configuration PostgreSQL
        self.pg_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'katooling_main_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
            'port': int(os.getenv('DB_PORT', 5432))
        }
        
        # Configuration SQLite
        self.sqlite_path = Path(os.getenv('SQLITE_PATH', 'backend/data/katula.db'))
        
        # Créer le dossier data s'il n'existe pas
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    def get_postgres_connection(self) -> psycopg2.extensions.connection:
        """Obtenir une connexion PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            return conn
        except psycopg2.Error as e:
            print(f"Erreur de connexion PostgreSQL: {e}")
            raise

    def get_sqlite_connection(self) -> sqlite3.Connection:
        """Obtenir une connexion SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row  # Pour avoir les résultats sous forme de dictionnaires
            return conn
        except sqlite3.Error as e:
            print(f"Erreur de connexion SQLite: {e}")
            raise

class DatabaseManager:
    """Gestionnaire des bases de données"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self._pg_conn = None
        self._sqlite_conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()

    @property
    def pg_conn(self) -> psycopg2.extensions.connection:
        """Connexion PostgreSQL avec création à la demande"""
        if self._pg_conn is None or self._pg_conn.closed:
            self._pg_conn = self.config.get_postgres_connection()
        return self._pg_conn

    @property
    def sqlite_conn(self) -> sqlite3.Connection:
        """Connexion SQLite avec création à la demande"""
        if self._sqlite_conn is None:
            self._sqlite_conn = self.config.get_sqlite_connection()
        return self._sqlite_conn

    def check_postgres_tables(self) -> list:
        """Vérifier les tables PostgreSQL"""
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            return [row[0] for row in cursor.fetchall()]

    def check_sqlite_tables(self) -> list:
        """Vérifier les tables SQLite"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def close_all(self):
        """Fermer toutes les connexions"""
        if self._pg_conn:
            self._pg_conn.close()
        if self._sqlite_conn:
            self._sqlite_conn.close()

def test_connections():
    """Tester les connexions aux bases de données"""
    try:
        with DatabaseManager() as db:
            print("=== Test des connexions aux bases de données ===")
            
            # Test PostgreSQL
            print("\nPostgreSQL:")
            tables = db.check_postgres_tables()
            print(f"Tables disponibles: {tables}")
            
            # Test SQLite
            print("\nSQLite:")
            tables = db.check_sqlite_tables()
            print(f"Tables disponibles: {tables}")
            
            print("\n✅ Test des connexions réussi!")
            return True
            
    except Exception as e:
        print(f"\n❌ Erreur lors du test des connexions: {str(e)}")
        return False

if __name__ == "__main__":
    test_connections()
