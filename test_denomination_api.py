#!/usr/bin/env python3
"""
Test de l'API des détails de dénomination
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def test_denomination_api():
    """Tester l'API des dénominations"""
    
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
        
        print("=== TEST API DENOMINATION ===")
        
        # Trouver quelques dénominations pour test
        cursor.execute("""
            SELECT univers, denomination, COUNT(*) as nb_combinations
            FROM combinations 
            WHERE alpha_ranking IS NOT NULL
            GROUP BY univers, denomination
            HAVING COUNT(*) > 1
            ORDER BY nb_combinations DESC
            LIMIT 5
        """)
        
        test_cases = cursor.fetchall()
        
        print("Cas de test trouvés:")
        for univers, denomination, nb_combinations in test_cases:
            print(f"  {univers} - {denomination}: {nb_combinations} combinations")
        
        # Tester le premier cas
        if test_cases:
            univers, denomination, nb_combinations = test_cases[0]
            
            print(f"\n=== TEST DETAILLE: {univers} - {denomination} ===")
            
            # Simuler l'appel API
            cursor.execute("""
                SELECT 
                    chip, forme, petique, tome, granque_name,
                    alpha_ranking
                FROM combinations
                WHERE univers = %s AND denomination = %s
                ORDER BY alpha_ranking ASC
            """, (univers, denomination))
            
            results = cursor.fetchall()
            
            print(f"Résultats API (triés par alpha-ranking):")
            for row in results:
                chip, forme, petique, tome, granque_name, alpha_ranking = row
                print(f"  {chip} - {forme} - α-rank: {alpha_ranking} - {petique}/{tome}/{granque_name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_denomination_api()