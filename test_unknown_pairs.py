
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.getcwd())
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.append(BASE_DIR)
sys.path.append(BACKEND_DIR)

from backend.app.services.pattern_recognition_service import PatternRecognitionService

def diagnose():
    db_url = "postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    service = PatternRecognitionService()
    
    # Test avec des numéros très improbables (probablement inconnus dans combinations)
    test_nums = [81, 82, 83, 84, 85]
    universes = ["mundo", "fruity"]
    
    for universe in universes:
        print(f"\n--- Diagnostic Univers: {universe} ---")
        
        # Vérifier si l'univers a des données dans combinations
        map_size = len(service._get_map(universe))
        print(f"Taille du mapping '{universe}' dans combinations: {map_size}")
        
        # Générer signature
        sig = service.generate_draw_signature(test_nums, universe)
        known_pairs = sum(1 for p in sig if any(v != "---" for v in p.values()))
        print(f"Paires connues pour [81-85]: {known_pairs}/10")
        
        # Rechercher matches
        results = service.find_similar_draws(db, test_nums, universe, min_match_percent=10)
        print(f"Matches trouvés (>=10%): {len(results.get('matches', []))}")
        
    db.close()

if __name__ == "__main__":
    diagnose()
