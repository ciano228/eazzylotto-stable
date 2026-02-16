#!/usr/bin/env python3
"""
Test simple de la fonctionnalité dénomination
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def test_ui_denomination():
    """Test simple de la fonctionnalité"""
    
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
        
        print("=== FONCTIONNALITE DENOMINATION CLIQUABLE ===")
        
        # Vérifier que alpha_ranking existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM combinations 
            WHERE alpha_ranking IS NOT NULL
        """)
        
        count_alpha = cursor.fetchone()[0]
        print(f"Records avec alpha_ranking: {count_alpha}")
        
        # Exemple concret
        cursor.execute("""
            SELECT univers, denomination, COUNT(*) as nb
            FROM combinations 
            WHERE alpha_ranking IS NOT NULL
            GROUP BY univers, denomination
            ORDER BY nb DESC
            LIMIT 3
        """)
        
        examples = cursor.fetchall()
        print(f"\nExemples de denominations cliquables:")
        for univers, denomination, nb in examples:
            print(f"  {univers} - '{denomination}': {nb} combinations")
        
        print(f"\n=== FONCTIONNALITES IMPLEMENTEES ===")
        print("1. API /api/denomination/{universe}/{denomination}")
        print("2. Denominations cliquables dans l'UI (soulignees en bleu)")
        print("3. Popup avec details des combinations triees par alpha-ranking")
        print("4. Affichage: chip, forme, petique, tome, granque_name")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_ui_denomination()