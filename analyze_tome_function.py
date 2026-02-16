#!/usr/bin/env python3
"""
Analyser en détail la fonction de calcul des tomes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def analyze_tome_calculation_detailed():
    """Analyser les conditions exactes pour tome11-14"""
    
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
        
        print("=== ANALYSE DETAILLEE FONCTION TOME ===")
        
        # 1. Rappel de la formule
        print("\nFORMULE TOME:")
        print("sigma = total_occurrences + somme(valeurs_granques_denominations_distinctes)")
        print("\nREGLES ACTUELLES:")
        print("1-19 -> tome1    |  50-59 -> tome5    |  90-99 -> tome10")
        print("20-29 -> tome2   |  60-69 -> tome6    |  100-109 -> tome11")
        print("30-39 -> tome3   |  70-79 -> tome7    |  110-119 -> tome12")
        print("40-49 -> tome4   |  80-89 -> tome8    |  120-129 -> tome13")
        print("                 |           -> tome9  |  130-139 -> tome14")
        
        # 2. Analyser les chips avec tome11-14
        high_tomes = ['tome11', 'tome12', 'tome13', 'tome14']
        
        for tome in high_tomes:
            print(f"\n=== ANALYSE {tome.upper()} ===")
            
            cursor.execute("""
                SELECT DISTINCT univers, chip
                FROM combinations 
                WHERE tome = %s
                ORDER BY univers, chip
            """, (tome,))
            
            chips_with_tome = cursor.fetchall()
            
            if chips_with_tome:
                print(f"Chips avec {tome}: {len(chips_with_tome)}")
                
                for univers, chip in chips_with_tome:
                    # Calculer sigma pour ce chip
                    cursor.execute("""
                        SELECT denomination, granque_name
                        FROM combinations
                        WHERE univers = %s AND chip = %s
                    """, (univers, chip))
                    
                    data = cursor.fetchall()
                    
                    # Compter occurrences
                    total_occurrences = len(data)
                    
                    # Dénominations distinctes et leurs granques
                    denominations_granques = {}
                    for denomination, granque_name in data:
                        if denomination not in denominations_granques:
                            granque_value = 0
                            if granque_name:
                                try:
                                    granque_value = int(granque_name.replace('Q', '').replace('q', ''))
                                except:
                                    granque_value = 0
                            denominations_granques[denomination] = granque_value
                    
                    sum_granques = sum(denominations_granques.values())
                    sigma = total_occurrences + sum_granques
                    
                    print(f"  {univers} {chip}:")
                    print(f"    Occurrences: {total_occurrences}")
                    print(f"    Denominations distinctes: {len(denominations_granques)}")
                    print(f"    Somme granques: {sum_granques}")
                    print(f"    Sigma: {sigma}")
                    print(f"    Granques detail: {list(denominations_granques.values())}")
            else:
                print(f"Aucun chip avec {tome}")
        
        # 3. Vérifier la logique de la formule
        print(f"\n=== VERIFICATION LOGIQUE FORMULE ===")
        
        def calculate_tome_from_sigma(sigma):
            """Reproduire la logique exacte"""
            if 1 <= sigma < 20:
                return "tome1"
            elif 20 <= sigma < 30:
                return "tome2"
            elif 30 <= sigma < 40:
                return "tome3"
            elif 40 <= sigma < 50:
                return "tome4"
            elif 50 <= sigma < 60:
                return "tome5"
            elif 60 <= sigma < 70:
                return "tome6"
            elif 70 <= sigma < 80:
                return "tome7"
            else:
                # PROBLEME POTENTIEL ICI
                return f"tome{(sigma // 10) + 1}"
        
        # Tester différentes valeurs de sigma
        test_sigmas = [79, 80, 85, 89, 90, 95, 99, 100, 105, 110, 115, 120, 125, 130, 135, 140]
        
        print("Test de la formule:")
        for sigma in test_sigmas:
            tome = calculate_tome_from_sigma(sigma)
            print(f"  sigma={sigma} -> {tome}")
        
        # 4. Identifier le problème dans la formule
        print(f"\n=== PROBLEME IDENTIFIE ===")
        print("La formule actuelle a un saut logique:")
        print("- 70-79 -> tome7")
        print("- 80+ -> tome{(sigma//10)+1}")
        print("  * sigma=80 -> tome{8+1} = tome9 (manque tome8)")
        print("  * sigma=90 -> tome{9+1} = tome10")
        print("  * sigma=100 -> tome{10+1} = tome11")
        print("  * sigma=130 -> tome{13+1} = tome14")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

def propose_corrected_formula():
    """Proposer une formule corrigée"""
    
    print(f"\n=== FORMULE CORRIGEE PROPOSEE ===")
    
    def corrected_tome_formula(sigma):
        """Formule corrigée sans saut"""
        if sigma < 1:
            return None
        elif 1 <= sigma < 20:
            return "tome1"
        elif 20 <= sigma < 30:
            return "tome2"
        elif 30 <= sigma < 40:
            return "tome3"
        elif 40 <= sigma < 50:
            return "tome4"
        elif 50 <= sigma < 60:
            return "tome5"
        elif 60 <= sigma < 70:
            return "tome6"
        elif 70 <= sigma < 80:
            return "tome7"
        elif 80 <= sigma < 90:
            return "tome8"
        elif 90 <= sigma < 100:
            return "tome9"
        else:
            # Pour sigma >= 100, continuer la progression
            return f"tome{(sigma // 10)}"
    
    print("FORMULE CORRIGEE:")
    print("1-19->tome1   50-59->tome5   90-99->tome9")
    print("20-29->tome2  60-69->tome6   100-109->tome10")
    print("30-39->tome3  70-79->tome7   110-119->tome11")
    print("40-49->tome4  80-89->tome8   120-129->tome12")
    print("                             130-139->tome13")
    print("                             140-149->tome14")
    
    # Test de la formule corrigée
    print(f"\nTEST FORMULE CORRIGEE:")
    test_sigmas = [79, 80, 85, 89, 90, 95, 99, 100, 105, 110, 115, 120, 125, 130, 135, 140]
    
    for sigma in test_sigmas:
        tome = corrected_tome_formula(sigma)
        print(f"  sigma={sigma} -> {tome}")

if __name__ == "__main__":
    analyze_tome_calculation_detailed()
    propose_corrected_formula()