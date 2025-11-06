#!/usr/bin/env python3
"""
Vérifier les colonnes exactes de la table_de_katula
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_katula_columns():
    """Vérifier la structure exacte de table_de_katula"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
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
        
        print("=== STRUCTURE TABLE_DE_KATULA ===\n")
        
        # Colonnes de la table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        print("COLONNES DISPONIBLES:")
        for col_name, data_type, nullable, default in columns:
            print(f"  - {col_name} ({data_type}) {'NULL' if nullable == 'YES' else 'NOT NULL'} {f'DEFAULT {default}' if default else ''}")
        
        # Échantillon de données
        cursor.execute("SELECT COUNT(*) FROM table_de_katula")
        total_count = cursor.fetchone()[0]
        print(f"\nTOTAL LIGNES: {total_count}")
        
        # Premiers échantillons
        cursor.execute("SELECT * FROM table_de_katula LIMIT 5")
        samples = cursor.fetchall()
        
        print("\nECHANTILLONS:")
        col_names = [desc[0] for desc in cursor.description]
        print(f"Colonnes: {col_names}")
        
        for i, sample in enumerate(samples):
            print(f"Ligne {i+1}: {dict(zip(col_names, sample))}")
        
        # Vérifier les univers
        if 'univers' in [col[0] for col in columns]:
            cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
            universes = [u[0] for u in cursor.fetchall()]
            print(f"\nUNIVERS DISPONIBLES: {universes}")
            
            # Pour chaque univers, voir la structure
            for univers in universes[:2]:  # Limiter à 2 pour l'exemple
                cursor.execute("SELECT COUNT(*) FROM table_de_katula WHERE univers = %s", (univers,))
                count = cursor.fetchone()[0]
                
                cursor.execute("SELECT * FROM table_de_katula WHERE univers = %s LIMIT 3", (univers,))
                samples = cursor.fetchall()
                
                print(f"\n{univers.upper()} ({count} lignes):")
                for sample in samples:
                    print(f"  {dict(zip(col_names, sample))}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_katula_columns()