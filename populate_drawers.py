#!/usr/bin/env python3
"""
Script de peuplement automatique des drawers
Logique: Parcourir univers par univers (mundo→fruity→trigga→roaster→sunshine)
Pour chaque chip (1→48), attribuer un drawer séquentiel aux formes peuplées
Ordre des formes: carre (haut) → triangle → losange → cercle (bas)
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

# Ordre des univers selon votre spécification
UNIVERS_ORDER = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']

# Ordre des formes du haut vers le bas dans un chip
FORME_ORDER = ['carre', 'triangle', 'losange', 'cercle']

def populate_drawers():
    """Peuple la colonne drawer selon la logique métier Katula"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== PEUPLEMENT DES DRAWERS ===\n")
    
    # 1. Créer la colonne si elle n'existe pas
    print("1. Creation de la colonne drawer...")
    cursor.execute("ALTER TABLE combinations ADD COLUMN IF NOT EXISTS drawer INTEGER")
    conn.commit()
    print("   [OK] Colonne drawer prete\n")
    
    # 2. Compteur global de drawer
    drawer_counter = 1
    total_updated = 0
    
    # 3. Parcourir chaque univers dans l'ordre
    for univers in UNIVERS_ORDER:
        print(f"Traitement univers: {univers}")
        
        # Parcourir les chips de 1 à 48
        for chip_num in range(1, 49):
            chip_id = f"chip{chip_num}"
            
            # Pour chaque forme dans l'ordre (haut → bas)
            for forme in FORME_ORDER:
                # Vérifier si ce drawer existe (a au moins une dénomination)
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM combinations
                    WHERE univers = %s 
                    AND chip = %s 
                    AND forme = %s
                    AND denomination IS NOT NULL 
                    AND denomination != ''
                    AND denomination != '---'
                """, (univers, chip_id, forme))
                
                result = cursor.fetchone()
                
                if result['count'] > 0:
                    # Ce drawer existe, lui attribuer le numéro
                    cursor.execute("""
                        UPDATE combinations
                        SET drawer = %s
                        WHERE univers = %s 
                        AND chip = %s 
                        AND forme = %s
                    """, (drawer_counter, univers, chip_id, forme))
                    
                    updated = cursor.rowcount
                    total_updated += updated
                    
                    print(f"   {chip_id} {forme:10} -> drawer {drawer_counter:4} ({updated} lignes)")
                    
                    # Incrémenter le compteur
                    drawer_counter += 1
                else:
                    # Drawer vide, on le saute
                    print(f"   {chip_id} {forme:10} -> VIDE (saute)")
        
        print(f"   Fin {univers}: drawer_counter = {drawer_counter - 1}\n")
    
    # 4. Commit final
    conn.commit()
    
    # 5. Statistiques finales
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
    
    # 6. Créer les index
    print("\n6. Creation des index...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_combinations_drawer ON combinations(drawer)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_combinations_univers_drawer ON combinations(univers, drawer)")
    conn.commit()
    print("   [OK] Index crees\n")
    
    cursor.close()
    conn.close()
    
    print("=== PEUPLEMENT TERMINE ===")

if __name__ == "__main__":
    try:
        populate_drawers()
    except Exception as e:
        print(f"\n[ERREUR]: {e}")
        import traceback
        traceback.print_exc()
