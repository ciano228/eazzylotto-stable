#!/usr/bin/env python3
"""
Test direct du service FormeService
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.services.forme_service import FormeService

def test_direct_service():
    """Test direct du service FormeService"""
    db = SessionLocal()
    
    try:
        universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
        
        for universe in universes:
            print(f"\n🌍 TEST SERVICE: {universe.upper()}")
            print("=" * 50)
            
            # Test avec session DB
            result = FormeService.get_formes_by_universe(universe, db)
            
            print(f"🎨 Formes: {result.get('formes', [])}")
            print(f"📈 Total: {result.get('total_formes', 0)}")
            print(f"🔧 Géométrie variable: {result.get('is_variable_geometry', False)}")
            print(f"📊 Counts: {result.get('forme_counts', {})}")
            
            if 'error' in result:
                print(f"❌ Erreur: {result['error']}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_service()