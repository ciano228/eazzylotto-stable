#!/usr/bin/env python3
"""
Peuplement CORRECT des drawers avec l'ORDRE METIER des formes
Ordre: carre, triangle, cercle, rectangle, puis formes composées
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

UNIVERS_ORDER = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']

# ORDRE METIER CORRECT des formes
FORME_ORDER = [
    'carre',
    'triangle', 
    'cercle',
    'rectangle',
    'carre-triangle',
    'carre-cercle',
    'carre-rectangle',
    'triangle-carre',
    'triangle-cercle',
    'triangle-rectangle',
    'cercle-carre',
    'cercle-triangle',
    'cercle-rectangle',
    'rectangle-carre',
    'rectangle-triangle',
    'rectangle-cercle'
]

def get_forme_order(forme):
    """Retourne l'ordre d'une forme selon la logique métier"""
    try:
        return FORME_ORDER.index(forme)
    except ValueError:
        return 999  # Formes inconnues à la fin

def populate_drawers_correct():
    """Peuple les drawers avec l'ordre métier correct"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== PEUPLEMENT DRAWERS (ORDRE METIER CORRECT) ===\n")
    
    # 1. Reset
    print("1. Reset drawer...")
    cursor.execute("UPDATE combinations SET drawer = NULL")
    conn.commit()
    print("   [OK]\n")
    
    # 2. Compteur global
    drawer_counter = 1
    total_updated = 0
    
    # 3. Pour chaque univers
    for univers in UNIVERS_ORDER:
        print(f"Traitement univers: {univers}")
        
        # Récupérer tous les chips avec leurs formes
        cursor.execute("""
            SELECT chip, forme
            FROM (
                SELECT DISTINCT chip, forme
                FROM combinations
                WHERE univers = %s 
                AND denomination IS NOT NULL 
                AND denomination != ''
                AND denomination != '---'
            ) sub
            ORDER BY CAST(SUBSTRING(chip FROM 5) AS INTEGER)
        """, (univers,))
        
        chip_formes = cursor.fetchall()
        
        if not chip_formes:
            print(f"   Aucun drawer pour {univers}\n")
            continue
        
        # Grouper par chip
        chips_dict = {}
        for row in chip_formes:
            chip = row['chip']
            forme = row['forme']
            if chip not in chips_dict:
                chips_dict[chip] = []
            chips_dict[chip].append(forme)
        
        # Pour chaque chip dans l'ordre
        for chip in sorted(chips_dict.keys(), key=lambda x: int(x.replace('chip', ''))):
            formes = chips_dict[chip]
            
            # Trier les formes selon l'ordre métier
            formes_sorted = sorted(formes, key=get_forme_order)
            
            # Attribuer drawer à chaque forme
            for forme in formes_sorted:
                cursor.execute("""
                    UPDATE combinations
                    SET drawer = %s
                    WHERE univers = %s 
                    AND chip = %s 
                    AND forme = %s
                """, (drawer_counter, univers, chip, forme))
                
                updated = cursor.rowcount
                total_updated += updated
                
                print(f"   {chip} {forme:20} -> drawer {drawer_counter:4} ({updated} lignes)")
                drawer_counter += 1
        
        print(f"   Fin {univers}: dernier drawer = {drawer_counter - 1}\n")
    
    # 4. Commit
    conn.commit()
    
    # 5. Stats
    cursor.execute("""
        SELECT 
            univers,
            COUNT(*) as total_rows,
            COUNT(DISTINCT drawer) as unique_drawers,
            MIN(drawer) as min_drawer,
            MAX(drawer) as max_drawer
        FROM combinations
        WHERE drawer IS NOT NULL
        GROUP BY univers
        ORDER BY 
            CASE univers
                WHEN 'mundo' THEN 1
                WHEN 'fruity' THEN 2
                WHEN 'trigga' THEN 3
                WHEN 'roaster' THEN 4
                WHEN 'sunshine' THEN 5
            END
    """)
    
    print("\n=== STATISTIQUES FINALES ===\n")
    for row in cursor.fetchall():
        print(f"{row['univers']:10} | Lignes: {row['total_rows']:5} | Drawers: {row['unique_drawers']:3} | Range: {row['min_drawer']}-{row['max_drawer']}")
    
    print(f"\nTotal lignes: {total_updated}")
    print(f"Dernier drawer: {drawer_counter - 1}")
    
    # 6. Vérification chip1 mundo
    print("\n=== VERIFICATION CHIP1 MUNDO ===\n")
    cursor.execute("""
        SELECT forme, denomination, drawer
        FROM combinations
        WHERE univers = 'mundo' AND chip = 'chip1'
        ORDER BY drawer
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        marker = " <-- SHOES 1" if row['denomination'] == 'shoes 1' else ""
        print(f"  drawer {row['drawer']}: {row['forme']:10} ({row['denomination']}){marker}")
    
    cursor.close()
    conn.close()
    
    print("\n=== TERMINE ===")

if __name__ == "__main__":
    try:
        populate_drawers_correct()
    except Exception as e:
        print(f"\n[ERREUR]: {e}")
        import traceback
        traceback.print_exc()
