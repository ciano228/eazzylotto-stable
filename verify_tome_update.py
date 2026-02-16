#!/usr/bin/env python3
"""
Vérifier que la mise à jour des tomes a bien fonctionné
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def verify_tome_update():
    """Vérifier les résultats de la mise à jour"""
    
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
        
        print("=== VERIFICATION MISE A JOUR TOMES ===")
        
        # 1. Distribution des tomes par univers
        for universe in ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']:
            print(f"\n--- {universe.upper()} ---")
            
            cursor.execute("""
                SELECT tome, COUNT(DISTINCT chip) as nb_chips, COUNT(*) as nb_occurrences
                FROM combinations 
                WHERE univers = %s AND tome IS NOT NULL
                GROUP BY tome
                ORDER BY tome
            """, (universe,))
            
            tome_stats = cursor.fetchall()
            
            if tome_stats:
                print("  Tomes utilisés:")
                for tome, nb_chips, nb_occurrences in tome_stats:
                    print(f"    {tome}: {nb_chips} chips, {nb_occurrences} occurrences")
            else:
                print("  Aucun tome défini")
        
        # 2. Vérifier quelques chips spécifiques
        print(f"\n=== VERIFICATION CHIPS SPECIFIQUES ===")
        
        test_cases = [
            ('mundo', 1),
            ('roaster', 31),  # Devrait être tome14
            ('sunshine', 25)  # Devrait être tome10
        ]
        
        for universe, chip_num in test_cases:
            cursor.execute("""
                SELECT DISTINCT tome
                FROM combinations 
                WHERE univers = %s AND chip = %s
            """, (universe, f'chip{chip_num}'))
            
            result = cursor.fetchone()
            tome = result[0] if result else "Non défini"
            print(f"{universe} chip{chip_num}: {tome}")
        
        # 3. Statistiques globales
        print(f"\n=== STATISTIQUES GLOBALES ===")
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT tome) as nb_tomes_distincts,
                COUNT(DISTINCT chip) as nb_chips_avec_tome,
                COUNT(*) as nb_total_occurrences
            FROM combinations 
            WHERE tome IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        nb_tomes, nb_chips, nb_occurrences = stats
        
        print(f"Tomes distincts: {nb_tomes}")
        print(f"Chips avec tome: {nb_chips}")
        print(f"Total occurrences: {nb_occurrences}")
        
        # 4. Tomes les plus élevés
        cursor.execute("""
            SELECT tome, COUNT(DISTINCT chip) as nb_chips
            FROM combinations 
            WHERE tome IS NOT NULL
            GROUP BY tome
            ORDER BY 
                CAST(SUBSTRING(tome FROM 'tome([0-9]+)') AS INTEGER) DESC
            LIMIT 5
        """)
        
        top_tomes = cursor.fetchall()
        print(f"\nTomes les plus élevés:")
        for tome, nb_chips in top_tomes:
            print(f"  {tome}: {nb_chips} chips")
        
        cursor.close()
        conn.close()
        
        print(f"\n=== VERIFICATION TERMINEE ===")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_tome_update()