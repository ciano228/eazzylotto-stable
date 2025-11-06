#!/usr/bin/env python3
"""
Vérifier les tables existantes dans la base de données
"""
import psycopg2

def verifier_tables():
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print("Tables disponibles dans la base de donnees:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Pour chaque table, voir sa structure
        for table in tables:
            table_name = table[0]
            print(f"\nStructure de la table '{table_name}':")
            
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
            
            # Compter les lignes
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  -> {count} lignes")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    verifier_tables()