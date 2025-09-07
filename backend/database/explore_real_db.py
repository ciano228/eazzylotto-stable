#!/usr/bin/env python3
"""
Explorer la vraie base de données katooling_main_system
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def explore_katooling_tables():
    """Explore les tables liées à KATOOLING"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Connexion
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        
        cursor = conn.cursor()
        
        # Chercher les tables avec 'katula' ou 'chip' dans le nom
        print("=== Tables KATOOLING/KATULA ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name ILIKE '%katula%' OR table_name ILIKE '%chip%' OR table_name ILIKE '%universe%')
            ORDER BY table_name;
        """)
        katula_tables = cursor.fetchall()
        
        for table in katula_tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Compter les lignes
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Lignes: {count}")
            
            # Voir la structure
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"  Colonnes: {', '.join([col[0] for col in columns[:5]])}...")
            
            # Voir quelques données
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                for i, row in enumerate(rows):
                    print(f"    Ligne {i+1}: {str(row)[:100]}...")
        
        # Chercher les tables de sessions
        print("\n=== Tables SESSIONS ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name ILIKE '%session%' OR table_name ILIKE '%draw%')
            ORDER BY table_name;
        """)
        session_tables = cursor.fetchall()
        
        for table in session_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} lignes")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    explore_katooling_tables()