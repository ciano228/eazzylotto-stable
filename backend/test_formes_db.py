#!/usr/bin/env python3
"""
Test direct des formes dans la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from sqlalchemy import text

def test_formes_in_db():
    """Test direct des formes dans la DB"""
    db = SessionLocal()
    
    try:
        universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
        
        for universe in universes:
            print(f"\n🌍 UNIVERS: {universe.upper()}")
            print("=" * 50)
            
            # Test 1: Vérifier si l'univers existe
            query_count = text("""
            SELECT COUNT(*) as total
            FROM combinations 
            WHERE univers = :universe
            """)
            
            result = db.execute(query_count, {"universe": universe})
            total = result.fetchone()[0]
            print(f"📊 Total combinaisons: {total}")
            
            if total > 0:
                # Test 2: Récupérer les formes distinctes
                query_formes = text("""
                SELECT DISTINCT forme, COUNT(*) as count
                FROM combinations 
                WHERE univers = :universe 
                AND forme IS NOT NULL 
                AND forme != ''
                GROUP BY forme
                ORDER BY forme
                """)
                
                result = db.execute(query_formes, {"universe": universe})
                formes = result.fetchall()
                
                print(f"🎨 Formes trouvées: {len(formes)}")
                for forme, count in formes:
                    print(f"  • {forme}: {count} occurrences")
                    
                # Test 3: Échantillon de données
                query_sample = text("""
                SELECT forme, denomination, chip
                FROM combinations 
                WHERE univers = :universe 
                AND forme IS NOT NULL 
                LIMIT 5
                """)
                
                result = db.execute(query_sample, {"universe": universe})
                samples = result.fetchall()
                
                print(f"📝 Échantillon de données:")
                for forme, denom, chip in samples:
                    print(f"  • Chip {chip}: {forme} -> {denom}")
            else:
                print("❌ Aucune donnée trouvée pour cet univers")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    test_formes_in_db()