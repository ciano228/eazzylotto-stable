#!/usr/bin/env python3
"""
Script pour tester les jointures parite et unidos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from app.models.combination import Combination
from app.models.parite import Parite
from app.models.unidos import Unidos
from sqlalchemy import text

def test_jointures():
    """Tester les jointures avec parite et unidos"""
    
    try:
        db = next(get_db())
        
        print("=== TEST DES JOINTURES ===")
        
        # Test 1: Vérifier quelques données de base
        print("\n1. Données dans combinations:")
        result = db.execute(text("""
            SELECT combination, parite_id, unidos_id 
            FROM combinations 
            WHERE parite_id IS NOT NULL AND unidos_id IS NOT NULL
            LIMIT 5
        """))
        
        for row in result:
            print(f"  {row[0]}: parite_id={row[1]}, unidos_id={row[2]}")
        
        # Test 2: Vérifier les données dans parite
        print("\n2. Données dans parite:")
        result = db.execute(text("SELECT parite_id, parite FROM parite LIMIT 5"))
        for row in result:
            print(f"  ID {row[0]}: {row[1]}")
        
        # Test 3: Vérifier les données dans unidos
        print("\n3. Données dans unidos:")
        result = db.execute(text("SELECT unidos_id, unidos FROM unidos LIMIT 5"))
        for row in result:
            print(f"  ID {row[0]}: {row[1]}")
        
        # Test 4: Test de jointure manuelle
        print("\n4. Test jointure manuelle:")
        result = db.execute(text("""
            SELECT c.combination, c.parite_id, p.parite, c.unidos_id, u.unidos
            FROM combinations c
            LEFT JOIN parite p ON c.parite_id = p.parite_id
            LEFT JOIN unidos u ON c.unidos_id = u.unidos_id
            WHERE c.parite_id IS NOT NULL AND c.unidos_id IS NOT NULL
            LIMIT 5
        """))
        
        for row in result:
            print(f"  {row[0]}: parite_id={row[1]} -> '{row[2]}', unidos_id={row[3]} -> '{row[4]}'")
        
        # Test 5: Test avec SQLAlchemy ORM
        print("\n5. Test avec SQLAlchemy ORM:")
        result = db.query(
            Combination.combination,
            Combination.parite_id,
            Parite.parite,
            Combination.unidos_id,
            Unidos.unidos
        ).outerjoin(
            Parite, Combination.parite_id == Parite.parite_id
        ).outerjoin(
            Unidos, Combination.unidos_id == Unidos.unidos_id
        ).limit(5).all()
        
        for row in result:
            print(f"  {row[0]}: parite_id={row[1]} -> '{row[2]}', unidos_id={row[3]} -> '{row[4]}'")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_jointures()