#!/usr/bin/env python3
"""
Test simple de connexion et génération de données
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_connection():
    """Test de base"""
    try:
        from app.database.connection import get_db
        db = next(get_db())
        print("Connexion DB OK")
        return True
    except Exception as e:
        print(f"Erreur connexion: {e}")
        return False

def test_session_service():
    """Test du service de session"""
    try:
        from app.services.session_service import SessionService
        from app.database.connection import get_db
        
        db = next(get_db())
        
        # Test récupération sessions
        sessions = SessionService.get_all_sessions(db)
        print(f"Sessions existantes: {len(sessions)}")
        
        for session in sessions:
            print(f"- {session.name} (ID: {session.id})")
        
        return True
        
    except Exception as e:
        print(f"Erreur service session: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_session():
    """Créer une session de test simple"""
    try:
        from app.services.session_service import SessionService
        from app.database.connection import get_db
        
        db = next(get_db())
        
        # Créer une session simple
        lottery_schedule = [
            {"name": "Test Loto", "day_offset": 0}
        ]
        
        session = SessionService.create_work_session(
            db=db,
            name="Session Test Simple",
            description="Test de base",
            lottery_type="Test",
            numbers_per_draw=6,
            number_range_min=1,
            number_range_max=49,
            total_draws=5,
            lottery_schedule=lottery_schedule,
            start_date=datetime.now() - timedelta(days=5),
            cycle_length=1
        )
        
        print(f"Session créée: {session.name} (ID: {session.id})")
        
        # Ajouter quelques tirages
        import random
        for i in range(1, 4):
            numbers = sorted(random.sample(range(1, 50), 6))
            SessionService.save_draw_numbers(
                db=db,
                session_id=session.id,
                draw_number=i,
                numbers=numbers,
                draw_date=datetime.now() - timedelta(days=5-i)
            )
            print(f"Tirage {i}: {numbers}")
        
        return True
        
    except Exception as e:
        print(f"Erreur création session: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("TEST SIMPLE DE CONNEXION ET DONNEES")
    print("=" * 40)
    
    if not test_basic_connection():
        return False
    
    if not test_session_service():
        return False
    
    if not create_simple_test_session():
        return False
    
    print("\nTEST REUSSI - Données de test créées!")
    return True

if __name__ == "__main__":
    main()