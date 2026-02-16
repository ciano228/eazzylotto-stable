#!/usr/bin/env python3
"""
Mise à jour des valeurs tome dans la BD selon la formule métier
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def calculate_tome_for_chip(cursor, chip_number, universe):
    """
    Calcule le tome pour un chip selon la formule :
    sigma = somme des occurrences sur le chip + somme des Q des dénominations distinctes
    
    Règles tome :
    1 <= sigma < 20 : tome1
    20 <= sigma < 30 : tome2  
    30 <= sigma < 40 : tome3
    40 <= sigma < 50 : tome4
    50 <= sigma < 60 : tome5
    etc...
    """
    
    # Récupérer toutes les combinaisons du chip
    cursor.execute("""
        SELECT denomination, granque_name
        FROM combinations
        WHERE chip = %s AND univers = %s
    """, (f'chip{chip_number}', universe))
    
    results = cursor.fetchall()
    
    if not results:
        return None, 0, []
    
    # Compter les occurrences totales
    total_occurrences = len(results)
    
    # Récupérer les dénominations distinctes et leurs granques
    denominations_granques = {}
    for denomination, granque_name in results:
        if denomination not in denominations_granques:
            # Extraire le numéro du granque (ex: "Q1" -> 1, "Q2" -> 2)
            granque_value = 0
            if granque_name:
                try:
                    granque_value = int(granque_name.replace('Q', '').replace('q', ''))
                except:
                    granque_value = 0
            denominations_granques[denomination] = granque_value
    
    # Calculer sigma
    sum_granques = sum(denominations_granques.values())
    sigma = total_occurrences + sum_granques
    
    # Déterminer le tome selon les règles
    if 1 <= sigma < 20:
        tome = "tome1"
    elif 20 <= sigma < 30:
        tome = "tome2"
    elif 30 <= sigma < 40:
        tome = "tome3"
    elif 40 <= sigma < 50:
        tome = "tome4"
    elif 50 <= sigma < 60:
        tome = "tome5"
    elif 60 <= sigma < 70:
        tome = "tome6"
    elif 70 <= sigma < 80:
        tome = "tome7"
    else:
        tome = f"tome{(sigma // 10) + 1}"
    
    return tome, sigma, list(denominations_granques.keys())

def update_tomes_in_database():
    """Met à jour les valeurs tome dans la BD"""
    
    load_dotenv()
    
    # Configuration BD
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
        
        print("=== MISE A JOUR DES TOMES ===")
        print("Formule: sigma = occurrences + somme(granques des dénominations distinctes)")
        print("Regles: 1-19->tome1, 20-29->tome2, 30-39->tome3, etc.")
        
        universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        
        for universe in universes:
            print(f"\n--- UNIVERS {universe.upper()} ---")
            
            corrections_count = 0
            
            for chip_number in range(1, 49):  # Chips 1-48
                calculated_tome, sigma, denominations = calculate_tome_for_chip(cursor, chip_number, universe)
                
                if calculated_tome is None:
                    continue
                
                # Récupérer le tome actuel dans la BD
                cursor.execute("""
                    SELECT DISTINCT tome FROM combinations
                    WHERE chip = %s AND univers = %s
                    LIMIT 1
                """, (f'chip{chip_number}', universe))
                
                result = cursor.fetchone()
                current_tome = result[0] if result else None
                
                if current_tome != calculated_tome:
                    print(f"Chip {chip_number}: {current_tome} -> {calculated_tome} (sigma={sigma})")
                    
                    # Mettre à jour toutes les combinaisons du chip
                    cursor.execute("""
                        UPDATE combinations 
                        SET tome = %s 
                        WHERE chip = %s AND univers = %s
                    """, (calculated_tome, f'chip{chip_number}', universe))
                    
                    corrections_count += 1
            
            if corrections_count > 0:
                print(f"OK {corrections_count} corrections appliquees pour {universe}")
            else:
                print(f"OK Aucune correction necessaire pour {universe}")
        
        # Valider les changements
        conn.commit()
        print(f"\nOK Toutes les mises a jour ont ete validees dans la BD")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_tome_calculation():
    """Test de quelques calculs de tome"""
    
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
        
        print("=== TEST CALCUL TOME ===")
        
        test_cases = [
            ('mundo', 1),
            ('fruity', 10), 
            ('trigga', 15),
            ('roaster', 20),
            ('sunshine', 25)
        ]
        
        for universe, chip_num in test_cases:
            tome, sigma, denominations = calculate_tome_for_chip(cursor, chip_num, universe)
            if tome:
                print(f"{universe} chip{chip_num}: sigma={sigma} -> {tome} ({len(denominations)} denominations)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur test: {e}")

if __name__ == "__main__":
    print("=== MISE A JOUR DES TOMES DANS LA BD ===")
    
    # Test d'abord
    test_tome_calculation()
    
    # Puis mise à jour
    update_tomes_in_database()
    
    print("\n=== MISE A JOUR TERMINEE ===")