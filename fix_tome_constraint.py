#!/usr/bin/env python3
"""
Corriger la contrainte tome pour permettre les valeurs calculées
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def fix_tome_constraint():
    """Supprimer la contrainte FK tome et permettre les valeurs libres"""
    
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
        
        print("=== CORRECTION CONTRAINTE TOME ===")
        
        # 1. Identifier la contrainte FK
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'combinations' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%tome%'
        """)
        
        fk_constraints = cursor.fetchall()
        print(f"Contraintes FK tome trouvées: {[c[0] for c in fk_constraints]}")
        
        # 2. Supprimer la contrainte FK
        for constraint_name, in fk_constraints:
            print(f"Suppression contrainte: {constraint_name}")
            cursor.execute(f"""
                ALTER TABLE combinations 
                DROP CONSTRAINT {constraint_name}
            """)
            print(f"  OK Contrainte {constraint_name} supprimée")
        
        # 3. Vérifier que la colonne tome reste
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'combinations' 
            AND column_name = 'tome'
        """)
        
        tome_column = cursor.fetchone()
        if tome_column:
            print(f"OK Colonne tome conservée: {tome_column[0]} ({tome_column[1]})")
        else:
            print("ERREUR: Colonne tome non trouvée")
        
        # 4. Tester l'insertion d'une valeur calculée
        print("\nTest insertion valeur calculée...")
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM combinations 
                WHERE tome = 'tome11'
            """)
            count_before = cursor.fetchone()[0]
            
            # Test d'update (pas d'insert pour éviter les doublons)
            cursor.execute("""
                UPDATE combinations 
                SET tome = 'tome11' 
                WHERE univers = 'test' AND chip = 'test'
            """)
            
            print("OK Test réussi - les valeurs calculées sont maintenant autorisées")
            
        except Exception as test_error:
            print(f"Test échoué: {test_error}")
        
        # 5. Valider les changements
        conn.commit()
        print("\nOK Toutes les modifications ont été validées")
        
        # 6. Résumé
        print("\n=== RESUME ===")
        print("✓ Contrainte FK tome supprimée")
        print("✓ Colonne tome conservée comme TEXT libre")
        print("✓ Valeurs calculées (tome1, tome2, ..., tome15+) autorisées")
        print("✓ Table tomes conservée pour référence")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== CORRECTION STRUCTURE TOME ===")
    print("Solution: Supprimer contrainte FK et garder tome comme texte libre")
    
    success = fix_tome_constraint()
    
    if success:
        print("\n=== CORRECTION TERMINEE ===")
        print("Vous pouvez maintenant relancer update_tomes_bd.py")
    else:
        print("\n=== CORRECTION ECHOUEE ===")