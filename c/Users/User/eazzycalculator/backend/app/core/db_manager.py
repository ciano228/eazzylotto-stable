"""
Module de gestion des connexions aux bases de données.
"""
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from typing import List, Dict, Any

class DatabaseManager:
    """Gestionnaire centralisé des connexions aux bases de données."""
    
    def __init__(self):
        """Initialise les connexions aux bases de données."""
        # SQLite connection (pour les données locales)
        self.sqlite_conn = sqlite3.connect("data/combinations.db")
        self.sqlite_conn.row_factory = sqlite3.Row

        # PostgreSQL connection (pour les données partagées)
        self.pg_conn = psycopg2.connect(
            dbname="katula_db",
            user="postgres",
            password="katula2024",
            host="localhost",
            port="5432",
            cursor_factory=DictCursor
        )

    def close_all(self):
        """Ferme toutes les connexions aux bases de données."""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()
        if hasattr(self, 'pg_conn'):
            self.pg_conn.close()

    def check_postgres_tables(self) -> List[str]:
        """Vérifie et retourne la liste des tables PostgreSQL."""
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            return [row[0] for row in cursor.fetchall()]

    def check_sqlite_tables(self) -> List[str]:
        """Vérifie et retourne la liste des tables SQLite."""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def get_chip_combinations(self, chip_id: int) -> List[Dict[str, Any]]:
        """Récupère les combinaisons pour un chip spécifique."""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM combinations WHERE chip = ?", (chip_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_chips(self) -> List[int]:
        """Récupère la liste de tous les chips disponibles."""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT DISTINCT chip FROM combinations ORDER BY chip")
        return [row[0] for row in cursor.fetchall()]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()
