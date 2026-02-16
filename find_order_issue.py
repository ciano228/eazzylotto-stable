#!/usr/bin/env python3
"""
Chercher des chips avec problème d'ordre des tiroirs
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def find_order_issues():
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
        
        # Vérifier l'ordre des formes dans la BD pour fruity
        print("=== ORDRE DES FORMES DANS LA BD ===")
        cursor.execute("""
            SELECT DISTINCT forme
            FROM combinations 
            WHERE univers = 'fruity'
            ORDER BY forme
        """)
        
        bd_forms = [row[0] for row in cursor.fetchall()]
        print("Formes BD fruity (ordre alphabétique):")
        for i, forme in enumerate(bd_forms, 1):
            print(f"  {i}. {forme}")
        
        # Ordre métier attendu
        expected_order = ['carre', 'triangle', 'cercle', 'rectangle']
        print(f"\nOrdre métier attendu: {expected_order}")
        
        # Vérifier si l'ordre BD correspond
        if bd_forms == sorted(expected_order):
            print("✓ L'ordre BD correspond à l'ordre métier trié")
        else:
            print("❌ Différence détectée")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    find_order_issues()