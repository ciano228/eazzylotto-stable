#!/usr/bin/env python3
"""
Vérifier les formes réelles de trigga dans la BD
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def check_trigga_forms():
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
        
        # Formes distinctes dans trigga
        cursor.execute("""
            SELECT DISTINCT forme
            FROM combinations 
            WHERE univers = 'trigga'
            ORDER BY forme
        """)
        
        trigga_forms = [row[0] for row in cursor.fetchall()]
        
        print("=== FORMES TRIGGA DANS LA BD ===")
        print(f"Nombre: {len(trigga_forms)}")
        for i, forme in enumerate(trigga_forms, 1):
            print(f"{i:2d}. {forme}")
        
        # Vérifier aussi fruity pour le problème d'ordre
        print("\n=== VERIFICATION ORDRE FRUITY ===")
        cursor.execute("""
            SELECT chip, forme, denomination
            FROM combinations 
            WHERE univers = 'fruity' AND forme = 'rectangle'
            ORDER BY chip
            LIMIT 5
        """)
        
        rectangle_data = cursor.fetchall()
        print("Échantillon rectangles fruity:")
        for chip, forme, denom in rectangle_data:
            print(f"  {chip}: {forme} -> {denom}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_trigga_forms()