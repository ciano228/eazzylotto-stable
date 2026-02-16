
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Chemins absolus
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

    print(f"--- Diagnostic Pattern Recognition ---")
    
    # 1. Vérifier les données
    count = db.execute(text("SELECT count(*) FROM session_draws")).scalar()
    print(f"Nombre de tirages en base: {count}")
    
    if count == 0:
        print("❌ AUCUN TIRAGE TROUVÉ ! L'analyse ne peut pas fonctionner.")
        return

    service = PatternRecognitionService()
    universe = "mundo"

    # Récupérer un tirage réel récent pour tester (au lieu de 5, 12...)
    recent_draw = db.execute(text("SELECT winning_numbers FROM session_draws ORDER BY draw_date DESC LIMIT 1")).fetchone()
    if recent_draw:
        test_nums = [int(n) for n in recent_draw[0]]
        print(f"Test avec le tirage le plus récent: {test_nums}")
    else:
        test_nums = [5, 12, 23, 45, 67]
        print(f"Test avec tirages génériques: {test_nums}")

    # 3. Tester la recherche
    print("\nRecherche de matches historiques...")
    for threshold in [20, 10, 5, 2, 0]:
        results = service.find_similar_draws(db, test_nums, universe, min_match_percent=threshold)
        matches = results.get("matches", [])
        print(f"Matches trouvés à {threshold}%: {len(matches)}")
        if matches:
            print(f"Meilleur score trouvé: {matches[0]['match_score']}%")
            # Voir pourquoi les scores sont bas
            if threshold == 0:
                print(f"Exemple de match top 1 (score {matches[0]['match_score']}%): {matches[0]['draw_numbers']}")
            if threshold > 0: break

    db.close()

if __name__ == "__main__":
    diagnose()
