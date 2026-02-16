#!/usr/bin/env python3
"""
Recherche directe dans la BD pour les dénominations multiples
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def search_multiple_denominations():
    load_dotenv()
    
    db_config = {
        'host': os.getenv('KATULA_DB_HOST', 'localhost'),
        'database': os.getenv('KATULA_DB_NAME', 'katooling_main_system'),
        'user': os.getenv('KATULA_DB_USER', 'postgres'),
        'password': os.getenv('KATULA_DB_PASSWORD', 'Katulaa_33'),
        'port': int(os.getenv('KATULA_DB_PORT', '5432'))
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Chercher toutes les dénominations contenant '/'
        cursor.execute("""
            SELECT univers, chip, forme, denomination, petique, tome, granque_name
            FROM combinations 
            WHERE denomination LIKE '%/%'
            ORDER BY univers, chip, forme
            LIMIT 20
        """)
        
        results = cursor.fetchall()
        
        print("=== DENOMINATIONS MULTIPLES TROUVEES ===")
        print(f"Nombre de résultats: {len(results)}")
        
        for row in results:
            univers, chip, forme, denomination, petique, tome, granque = row
            print(f"{univers} - {chip} - {forme}: '{denomination}'")
            
            if '/' in denomination:
                parts = denomination.split('/')
                print(f"  -> Parties: {[p.strip() for p in parts]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur BD: {e}")

if __name__ == "__main__":
    search_multiple_denominations()