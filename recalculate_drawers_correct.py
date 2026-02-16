#!/usr/bin/env python3
"""
Recalcul CORRECT des drawers basé sur l'analyse réelle de la BD
Utilise les VRAIES formes: carre, triangle, rectangle, cercle
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
FORME_ORDER = ['carre', 'triangle', 'rectangle', 'cercle']

def recalculate_drawers():
    """Recalcule les drawers basé sur les VRAIES données BD"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== RECALCUL CORRECT DES DRAWERS ===\n")
    
    # 1. Reset drawer
    print("1. Reset drawer a NULL...")
    cursor.execute("UPDATE combinations SET drawer = NULL")
    conn.commit()
    print("   [OK]\n")
    
    # 2. Compteur global
    drawer_counter = 1
    total_updated = 0
    
    # 3. Pour chaque univers
    for univers in UNIVERS_ORDER:
        print(f"Traitement univers: {univers}")
        
        # Récupérer tous les chips avec leurs formes peuplées
        cursor.execute("""
            SELECT 
                chip,
                array_agg(forme ORDER BY 
                    CASE forme
                        WHEN 'carre' THEN 1
                        WHEN 'triangle' THEN 2
                        WHEN 'rectangle' THEN 3
                        WHEN 'cercle' THEN 4
                    END
                ) as formes_list
            FROM (
                SELECT DISTINCT chip, forme
                FROM combinations
                WHERE univers = %s 
                AND denomination IS NOT NULL 
                AND denomination != ''
                AND denomination != '---'
            ) sub
            GROUP BY chip
            ORDER BY 
                CAST(SUBSTRING(chip FROM 5) AS INTEGER)
        """, (univers,))
        
        chips_data = cursor.fetchall()
        
        if not chips_data:
            print(f"   Aucun drawer pour {univers}\n")
            continue
        
        # Pour chaque chip
        for chip_row in chips_data:
            chip = chip_row['chip']
            formes = chip_row['formes_list']
            
            # Pour chaque forme peuplée dans l'ordre
            for forme in formes:
                # Attribuer le drawer
                cursor.execute("""
                    UPDATE combinations
                    SET drawer = %s
                    WHERE univers = %s 
                    AND chip = %s 
                    AND forme = %s
                """, (drawer_counter, univers, chip, forme))
                
                updated = cursor.rowcount
                total_updated += updated
                
                print(f"   {chip} {forme:10} -> drawer {drawer_counter:4} ({updated} lignes)")
                drawer_counter += 1
        
        print(f"   Fin {univers}: dernier drawer = {drawer_counter - 1}\n")
    
    # 4. Commit
    conn.commit()
    
    # 5. Statistiques
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
    
    print(f"\nTotal lignes mises a jour: {total_updated}")
    print(f"Dernier drawer attribue: {drawer_counter - 1}")
    
    # 6. Vérification mundo
    cursor.execute("""
        SELECT 
            chip,
            COUNT(DISTINCT drawer) as drawer_count
        FROM combinations
        WHERE univers = 'mundo' AND drawer IS NOT NULL
        GROUP BY chip
        HAVING COUNT(DISTINCT drawer) IN (1, 2, 3)
        ORDER BY drawer_count, chip
    """)
    
    special = cursor.fetchall()
    c1 = [r['chip'] for r in special if r['drawer_count'] == 1]
    c2 = [r['chip'] for r in special if r['drawer_count'] == 2]
    c3 = [r['chip'] for r in special if r['drawer_count'] == 3]
    
    print(f"\nVerification mundo:")
    print(f"  1 drawer: {len(c1)} chips")
    print(f"  2 drawers: {len(c2)} chips")
    print(f"  3 drawers: {len(c3)} chips")
    
    cursor.close()
    conn.close()
    
    print("\n=== RECALCUL TERMINE ===")

if __name__ == "__main__":
    try:
        recalculate_drawers()
    except Exception as e:
        print(f"\n[ERREUR]: {e}")
        import traceback
        traceback.print_exc()
