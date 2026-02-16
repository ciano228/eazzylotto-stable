#!/usr/bin/env python3
"""
Test de la colonne drawer dans la table combinations
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

def test_drawer_column():
    """Vérifie si la colonne drawer existe et contient des données"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== TEST COLONNE DRAWER ===\n")
    
    # 1. Vérifier si la colonne existe
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'combinations' 
        AND column_name = 'drawer'
    """)
    
    col_info = cursor.fetchone()
    if col_info:
        print(f"[OK] Colonne 'drawer' existe: {col_info['data_type']}")
    else:
        print("[ERREUR] Colonne 'drawer' N'EXISTE PAS dans la table combinations")
        print("\nSolution: Ajouter la colonne avec:")
        print("   ALTER TABLE combinations ADD COLUMN drawer INTEGER;")
        conn.close()
        return
    
    # 2. Compter les valeurs non-nulles
    cursor.execute("SELECT COUNT(*) as total, COUNT(drawer) as with_drawer FROM combinations")
    counts = cursor.fetchone()
    print(f"\nStatistiques:")
    print(f"   Total lignes: {counts['total']}")
    print(f"   Avec drawer: {counts['with_drawer']}")
    print(f"   Sans drawer (NULL): {counts['total'] - counts['with_drawer']}")
    
    # 3. Exemples de données
    cursor.execute("""
        SELECT univers, chip, forme, denomination, drawer 
        FROM combinations 
        WHERE drawer IS NOT NULL 
        LIMIT 10
    """)
    
    print(f"\nExemples (10 premieres lignes avec drawer):")
    for row in cursor.fetchall():
        print(f"   {row['univers']:8} | chip={row['chip']:6} | forme={row['forme']:10} | denom={row['denomination']:15} | drawer={row['drawer']}")
    
    # 4. Distribution des drawers par univers
    cursor.execute("""
        SELECT univers, COUNT(DISTINCT drawer) as unique_drawers, 
               MIN(drawer) as min_drawer, MAX(drawer) as max_drawer
        FROM combinations 
        WHERE drawer IS NOT NULL
        GROUP BY univers
        ORDER BY univers
    """)
    
    print(f"\nDistribution par univers:")
    for row in cursor.fetchall():
        print(f"   {row['univers']:8} | Drawers uniques: {row['unique_drawers']:3} | Range: {row['min_drawer']}-{row['max_drawer']}")
    
    # 5. Vérifier chip5 mundo (cas spécial mentionné)
    cursor.execute("""
        SELECT chip, forme, denomination, drawer 
        FROM combinations 
        WHERE univers = 'mundo' AND chip = 'chip5'
        ORDER BY drawer
    """)
    
    print(f"\nCas special chip5 mundo (drawers incomplets):")
    chip5_rows = cursor.fetchall()
    if chip5_rows:
        for row in chip5_rows:
            print(f"   forme={row['forme']:10} | denom={row['denomination']:15} | drawer={row['drawer']}")
    else:
        print("   [WARN] Aucune donnee pour chip5 mundo")
    
    conn.close()
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    try:
        test_drawer_column()
    except Exception as e:
        print(f"\n[ERREUR]: {e}")
        import traceback
        traceback.print_exc()
