#!/usr/bin/env python3
"""
Créer les tomes manquants dans la table tomes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def create_missing_tomes():
    """Créer les tomes manquants jusqu'à tome15"""
    
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
        
        print("=== CREATION DES TOMES MANQUANTS ===")
        
        # Vérifier les tomes existants
        cursor.execute("SELECT name FROM tomes ORDER BY name")
        existing_tomes = [row[0] for row in cursor.fetchall()]
        print(f"Tomes existants: {existing_tomes}")
        
        # Créer les tomes manquants jusqu'à tome15
        tomes_to_create = []
        for i in range(1, 16):  # tome1 à tome15
            tome_name = f"tome{i}"
            if tome_name not in existing_tomes:
                tomes_to_create.append(tome_name)
        
        if tomes_to_create:
            print(f"Tomes à créer: {tomes_to_create}")
            
            for tome_name in tomes_to_create:
                cursor.execute("""
                    INSERT INTO tomes (name, description) 
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (tome_name, f"Tome {tome_name.replace('tome', '')} - Auto-généré"))
                
                print(f"  + {tome_name} créé")
            
            conn.commit()
            print(f"OK {len(tomes_to_create)} tomes créés")
        else:
            print("OK Tous les tomes nécessaires existent déjà")
        
        # Vérifier après création
        cursor.execute("SELECT name FROM tomes ORDER BY name")
        final_tomes = [row[0] for row in cursor.fetchall()]
        print(f"Tomes finaux: {final_tomes}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_missing_tomes()