#!/usr/bin/env python3
"""
Analyse de la structure réelle des drawers dans la BD
Pour comprendre combien de drawers par chip et par univers
"""
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def analyze_drawer_structure():
    """Analyse la structure réelle des drawers"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== ANALYSE STRUCTURE DRAWERS ===\n")
    
    # Pour chaque univers
    univers_list = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    for univers in univers_list:
        print(f"\n{'='*60}")
        print(f"UNIVERS: {univers.upper()}")
        print(f"{'='*60}")
        
        # Compter les chips avec drawers
        cursor.execute("""
            SELECT 
                chip,
                COUNT(DISTINCT forme) as formes_count,
                array_agg(DISTINCT forme ORDER BY forme) as formes_list
            FROM combinations
            WHERE univers = %s 
            AND denomination IS NOT NULL 
            AND denomination != ''
            AND denomination != '---'
            GROUP BY chip
            ORDER BY chip
        """, (univers,))
        
        chips_data = cursor.fetchall()
        
        if not chips_data:
            print(f"  Aucun drawer pour {univers}")
            continue
        
        # Statistiques
        chips_with_2_drawers = []
        chips_with_3_drawers = []
        chips_with_4_drawers = []
        chips_with_1_drawer = []
        
        for row in chips_data:
            chip = row['chip']
            count = row['formes_count']
            formes = row['formes_list']
            
            if count == 1:
                chips_with_1_drawer.append(chip)
            elif count == 2:
                chips_with_2_drawers.append(chip)
            elif count == 3:
                chips_with_3_drawers.append(chip)
            elif count == 4:
                chips_with_4_drawers.append(chip)
        
        print(f"\nStatistiques {univers}:")
        print(f"  Total chips avec drawers: {len(chips_data)}")
        print(f"  Chips avec 1 drawer: {len(chips_with_1_drawer)}")
        print(f"  Chips avec 2 drawers: {len(chips_with_2_drawers)}")
        print(f"  Chips avec 3 drawers: {len(chips_with_3_drawers)}")
        print(f"  Chips avec 4 drawers: {len(chips_with_4_drawers)}")
        
        if chips_with_1_drawer:
            print(f"\n  Chips 1 drawer: {', '.join(chips_with_1_drawer)}")
        if chips_with_2_drawers:
            print(f"  Chips 2 drawers: {', '.join(chips_with_2_drawers)}")
        if chips_with_3_drawers:
            print(f"  Chips 3 drawers: {', '.join(chips_with_3_drawers)}")
        if chips_with_4_drawers:
            print(f"  Chips 4 drawers: {', '.join(chips_with_4_drawers)}")
        
        # Détail pour mundo
        if univers == 'mundo':
            print(f"\n  Detail mundo (premiers 10 chips):")
            for row in chips_data[:10]:
                print(f"    {row['chip']}: {row['formes_count']} formes -> {row['formes_list']}")
    
    # Vérification spécifique mundo
    print(f"\n\n{'='*60}")
    print("VERIFICATION MUNDO (selon vos specs)")
    print(f"{'='*60}")
    
    cursor.execute("""
        SELECT 
            chip,
            COUNT(DISTINCT forme) as drawer_count,
            array_agg(DISTINCT forme ORDER BY forme) as formes
        FROM combinations
        WHERE univers = 'mundo'
        AND denomination IS NOT NULL 
        AND denomination != ''
        AND denomination != '---'
        GROUP BY chip
        HAVING COUNT(DISTINCT forme) IN (2, 3)
        ORDER BY chip
    """)
    
    special_chips = cursor.fetchall()
    
    chips_2 = [r['chip'] for r in special_chips if r['drawer_count'] == 2]
    chips_3 = [r['chip'] for r in special_chips if r['drawer_count'] == 3]
    
    print(f"\nChips mundo avec 2 drawers: {len(chips_2)}")
    print(f"  {', '.join(chips_2)}")
    print(f"\nChips mundo avec 3 drawers: {len(chips_3)}")
    print(f"  {', '.join(chips_3)}")
    
    print(f"\nVotre spec: 13 chips avec 2 drawers, 7 chips avec 3 drawers")
    print(f"BD actuelle: {len(chips_2)} chips avec 2 drawers, {len(chips_3)} chips avec 3 drawers")
    
    if len(chips_2) == 13 and len(chips_3) == 7:
        print("\n[OK] Les donnees correspondent a vos specs!")
    else:
        print("\n[ATTENTION] Difference avec vos specs!")
    
    conn.close()
    print("\n=== FIN ANALYSE ===")

if __name__ == "__main__":
    try:
        analyze_drawer_structure()
    except Exception as e:
        print(f"\n[ERREUR]: {e}")
        import traceback
        traceback.print_exc()
