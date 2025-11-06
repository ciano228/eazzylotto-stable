#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table combinations et les chips
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from sqlalchemy import text

def check_chip_structure():
    """Vérifier la structure des chips et combinations"""
    
    try:
        db = next(get_db())
        
        print("=== STRUCTURE TABLE CHIPS ===")
        result = db.execute(text("SELECT * FROM chips LIMIT 5"))
        rows = result.fetchall()
        print("Colonnes:", result.keys())
        for row in rows:
            print(f"  ID: {row[0]}, Nom: {row[1]}, Description: {row[2]}")
        
        print("\n=== STRUCTURE TABLE COMBINATIONS (COLONNES) ===")
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'combinations' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        chip_column_found = False
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
            if 'chip' in col[0].lower():
                chip_column_found = True
                print(f"    *** COLONNE CHIP TROUVÉE: {col[0]} ***")
        
        if not chip_column_found:
            print("  ❌ Aucune colonne chip trouvée dans combinations")
        
        print("\n=== ÉCHANTILLON COMBINATIONS AVEC CHIP (si existe) ===")
        try:
            result = db.execute(text("SELECT combination, chip_id FROM combinations WHERE chip_id IS NOT NULL LIMIT 10"))
            for row in result:
                print(f"  {row[0]}: chip_id={row[1]}")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            print("  La colonne chip_id n'existe probablement pas dans combinations")
        
        print("\n=== JOINTURE TEST COMBINATIONS + CHIPS ===")
        try:
            result = db.execute(text("""
                SELECT c.combination, ch.chip_name 
                FROM combinations c 
                LEFT JOIN chips ch ON c.chip_id = ch.chip_id 
                WHERE c.chip_id IS NOT NULL 
                LIMIT 5
            """))
            for row in result:
                print(f"  {row[0]}: {row[1]}")
        except Exception as e:
            print(f"  ❌ Erreur jointure: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    check_chip_structure()