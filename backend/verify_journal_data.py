# -*- coding: utf-8 -*-
"""
Script de verification du journal pour le tirage du 14-02-2025
Compare les donnees PostgreSQL avec celles affichees
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from itertools import combinations
import json
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def get_draw_data():
    """Recupere le tirage du 14-02-2025"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT *
        FROM draws
        WHERE draw_date = '2025-02-14'
        ORDER BY id DESC
        LIMIT 1
    """)
    
    draw = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return dict(draw) if draw else None

def get_combination_data(num1, num2, universe=None):
    """Recupere les donnees d'une combinaison depuis PostgreSQL"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            combination_id, num1, num2, univers, forme, 
            granque_name, petique, tome, denomination,
            engine, beastie, chip, ligne, colonne,
            alpha_ranking, parite_id, unidos_id, chip_id,
            quartier, region, combination
        FROM combinations 
        WHERE num1 = %s AND num2 = %s
    """
    
    params = [num1, num2]
    
    if universe:
        query += " AND univers = %s"
        params.append(universe)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(result) if result else None

def verify_journal():
    """Verifie le journal pour le tirage du 14-02-2025"""
    
    print("=" * 80)
    print("VERIFICATION DU JOURNAL - Tirage du 14-02-2025")
    print("=" * 80)
    
    draw = get_draw_data()
    
    if not draw:
        print("\nERREUR: Tirage du 14-02-2025 non trouve dans la BD")
        print("\nUtilisation de numeros de test: [1, 2, 3, 4, 5]")
        winning_numbers = [1, 2, 3, 4, 5]
    else:
        print(f"\nTirage trouve:")
        print(f"   - Date: {draw['draw_date']}")
        print(f"   - Loterie: {draw.get('lottery_name', 'N/A')}")
        print(f"   - Numeros: {draw.get('winning_numbers', [])}")
        
        winning_numbers = draw.get('winning_numbers', [])
        if not winning_numbers or len(winning_numbers) < 2:
            print("\nPas assez de numeros gagnants, utilisation de test: [1, 2, 3, 4, 5]")
            winning_numbers = [1, 2, 3, 4, 5]
    
    combos = list(combinations(winning_numbers, 2))
    
    print(f"\nAnalyse de {len(combos)} combinaisons:")
    print("-" * 80)
    
    universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    for universe in universes:
        print(f"\nUNIVERS: {universe.upper()}")
        print("-" * 80)
        
        found_count = 0
        
        for num1, num2 in combos:
            combo_data = get_combination_data(num1, num2, universe)
            
            if combo_data:
                found_count += 1
                print(f"\nCombinaison {num1}-{num2}:")
                print(f"   - Univers: {combo_data['univers']}")
                print(f"   - Forme: {combo_data['forme']}")
                print(f"   - Denomination: {combo_data['denomination']}")
                print(f"   - Granque: {combo_data['granque_name']}")
                print(f"   - Petique: {combo_data['petique']}")
                print(f"   - Tome: {combo_data['tome']}")
                print(f"   - Ligne: {combo_data['ligne']}")
                print(f"   - Colonne: {combo_data['colonne']}")
                print(f"   - Alpha Ranking: {combo_data['alpha_ranking']}")
                print(f"   - Engine: {combo_data['engine']}")
                print(f"   - Beastie: {combo_data['beastie']}")
                print(f"   - Chip: {combo_data['chip']}")
                print(f"   - Parite ID: {combo_data['parite_id']}")
                print(f"   - Unidos ID: {combo_data['unidos_id']}")
        
        if found_count == 0:
            print(f"   NO-HOLD: Aucune combinaison trouvee pour l'univers {universe}")
        else:
            print(f"\n   Total: {found_count}/{len(combos)} combinaisons trouvees")
    
    print("\n" + "=" * 80)
    print("RESUME - DONNEES ATTENDUES DANS LE JOURNAL")
    print("=" * 80)
    
    print("\nPour chaque univers, le journal doit afficher:")
    print("   - Si combinaisons trouvees -> Afficher les VRAIES donnees PostgreSQL")
    print("   - Si aucune combinaison -> Afficher 'NO-HOLD' (pas de prise)")
    print("\nIMPORTANT:")
    print("   - Pas de donnees fictives (Alpha-1, L6, C2, Pair/Impair calcule)")
    print("   - Utiliser UNIQUEMENT les valeurs de la BD")
    print("   - Filtrer par univers selectionne")

if __name__ == "__main__":
    verify_journal()
