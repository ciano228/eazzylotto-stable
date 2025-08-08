#!/usr/bin/env python3
"""
Générateur de données de test pour EazzyLotto
Crée des sessions avec tirages simulés pour tester les fonctionnalités
"""

import random
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_lottery_numbers(count: int, min_num: int = 1, max_num: int = 90) -> List[int]:
    """Générer des numéros de loterie aléatoires"""
    return sorted(random.sample(range(min_num, max_num + 1), count))

def create_test_sessions():
    """Créer des sessions de test avec données simulées"""
    
    try:
        from app.database.connection import get_db
        from app.services.session_service import SessionService
        
        db = next(get_db())
        
        # Session 1: Loto Français (6/49)
        print("Creation Session 1: Loto Francais...")
        
        lottery_schedule_fr = [
            {"name": "Loto Lundi", "day_offset": 0},
            {"name": "Loto Mercredi", "day_offset": 2}, 
            {"name": "Loto Samedi", "day_offset": 5}
        ]
        
        session1 = SessionService.create_work_session(
            db=db,
            name="Session Test - Loto Français",
            description="Données de test pour le Loto Français 6/49",
            lottery_type="Loto Français",
            numbers_per_draw=6,
            number_range_min=1,
            number_range_max=49,
            total_draws=18,  # 6 semaines de tirages
            lottery_schedule=lottery_schedule_fr,
            start_date=datetime.now() - timedelta(days=42),
            cycle_length=7
        )
        
        # Remplir avec des numéros aléatoires
        for i in range(1, 16):  # 15 tirages complétés
            numbers = generate_lottery_numbers(6, 1, 49)
            SessionService.save_draw_numbers(
                db=db,
                session_id=session1.id,
                draw_number=i,
                numbers=numbers,
                draw_date=datetime.now() - timedelta(days=42-i*3)
            )
        
        print(f"Session 1 creee (ID: {session1.id}) avec 15 tirages")
        
        # Session 2: EuroMillions (5/50 + 2/12)
        print("Creation Session 2: EuroMillions...")
        
        lottery_schedule_euro = [
            {"name": "EuroMillions Mardi", "day_offset": 1},
            {"name": "EuroMillions Vendredi", "day_offset": 4}
        ]
        
        session2 = SessionService.create_work_session(
            db=db,
            name="Session Test - EuroMillions",
            description="Données de test pour EuroMillions 5/50",
            lottery_type="EuroMillions",
            numbers_per_draw=5,
            number_range_min=1,
            number_range_max=50,
            total_draws=12,  # 6 semaines
            lottery_schedule=lottery_schedule_euro,
            start_date=datetime.now() - timedelta(days=35),
            cycle_length=7
        )
        
        # Remplir avec des numéros aléatoires
        for i in range(1, 11):  # 10 tirages complétés
            numbers = generate_lottery_numbers(5, 1, 50)
            SessionService.save_draw_numbers(
                db=db,
                session_id=session2.id,
                draw_number=i,
                numbers=numbers,
                draw_date=datetime.now() - timedelta(days=35-i*3)
            )
        
        print(f"Session 2 creee (ID: {session2.id}) avec 10 tirages")
        
        # Session 3: Loto US (6/90) - Plus complexe
        print("Creation Session 3: Loto US...")
        
        lottery_schedule_us = [
            {"name": "PowerBall Lundi", "day_offset": 0},
            {"name": "PowerBall Mercredi", "day_offset": 2},
            {"name": "PowerBall Samedi", "day_offset": 5}
        ]
        
        session3 = SessionService.create_work_session(
            db=db,
            name="Session Test - Loto US",
            description="Données de test pour Loto US 6/90 avec patterns complexes",
            lottery_type="Loto US",
            numbers_per_draw=6,
            number_range_min=1,
            number_range_max=90,
            total_draws=21,  # 7 semaines
            lottery_schedule=lottery_schedule_us,
            start_date=datetime.now() - timedelta(days=49),
            cycle_length=7
        )
        
        # Remplir avec des numéros incluant quelques patterns
        for i in range(1, 19):  # 18 tirages complétés
            if i % 5 == 0:  # Tous les 5 tirages, créer un pattern
                # Pattern: numéros consécutifs
                start_num = random.randint(1, 85)
                numbers = list(range(start_num, start_num + 6))
            elif i % 7 == 0:  # Tous les 7 tirages, No Draw
                numbers = []
                SessionService.save_draw_numbers(
                    db=db,
                    session_id=session3.id,
                    draw_number=i,
                    numbers=numbers,
                    draw_date=datetime.now() - timedelta(days=49-i*2),
                    is_no_draw=True
                )
                continue
            else:
                numbers = generate_lottery_numbers(6, 1, 90)
            
            SessionService.save_draw_numbers(
                db=db,
                session_id=session3.id,
                draw_number=i,
                numbers=numbers,
                draw_date=datetime.now() - timedelta(days=49-i*2)
            )
        
        print(f"Session 3 creee (ID: {session3.id}) avec 18 tirages (incluant patterns)")
        
        # Session 4: Keno (10/80) - Rapide
        print("Creation Session 4: Keno...")
        
        lottery_schedule_keno = [
            {"name": "Keno Quotidien", "day_offset": 0}
        ]
        
        session4 = SessionService.create_work_session(
            db=db,
            name="Session Test - Keno",
            description="Données de test pour Keno 10/80 quotidien",
            lottery_type="Keno",
            numbers_per_draw=10,
            number_range_min=1,
            number_range_max=80,
            total_draws=30,  # 30 jours
            lottery_schedule=lottery_schedule_keno,
            start_date=datetime.now() - timedelta(days=30),
            cycle_length=1
        )
        
        # Remplir avec des numéros aléatoires
        for i in range(1, 26):  # 25 tirages complétés
            numbers = generate_lottery_numbers(10, 1, 80)
            SessionService.save_draw_numbers(
                db=db,
                session_id=session4.id,
                draw_number=i,
                numbers=numbers,
                draw_date=datetime.now() - timedelta(days=30-i)
            )
        
        print(f"Session 4 creee (ID: {session4.id}) avec 25 tirages")
        
        # Activer la première session par défaut
        SessionService.activate_session(db, session1.id)
        
        print("\nDONNEES DE TEST GENEREES AVEC SUCCES!")
        print("=" * 50)
        print("Sessions créées:")
        print(f"1. Loto Français (6/49) - {session1.id} - 15/18 tirages")
        print(f"2. EuroMillions (5/50) - {session2.id} - 10/12 tirages") 
        print(f"3. Loto US (6/90) - {session3.id} - 18/21 tirages")
        print(f"4. Keno (10/80) - {session4.id} - 25/30 tirages")
        print(f"\nSession active: {session1.name}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_analysis_data():
    """Générer des données d'analyse pour les tests"""
    
    try:
        from app.database.connection import get_db
        from app.models.analysis import CombinationAnalysis
        
        db = next(get_db())
        
        print("Generation des donnees d'analyse...")
        
        # Générer des analyses pour différents univers
        universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
        
        for universe in universes:
            for i in range(50):  # 50 analyses par univers
                combination = generate_lottery_numbers(2, 1, 90)
                
                analysis = CombinationAnalysis(
                    combination=combination,
                    universe=universe,
                    chip=random.randint(1, 45),
                    denomination=f"D{random.randint(1, 15)}",
                    granque=f"G{random.randint(1, 9)}",
                    petique=f"P{random.randint(1, 5)}",
                    ligne=random.randint(1, 9),
                    colonne=random.randint(1, 5),
                    parite=random.choice(["pair", "impair", "mixte"]),
                    unidos=f"U{random.randint(1, 10)}",
                    forme=random.choice(["carre", "triangle", "cercle", "rectangle"]),
                    engine=random.choice(["car", "train", "plane", "boat"]),
                    beastie=random.choice(["lion", "tiger", "bear", "eagle"]),
                    tome=f"tome{random.randint(1, 5)}"
                )
                
                db.add(analysis)
        
        db.commit()
        print("Donnees d'analyse generees")
        
        return True
        
    except Exception as e:
        print(f"Erreur generation analyse: {e}")
        return False

def main():
    """Fonction principale"""
    print("GENERATEUR DE DONNEES DE TEST EAZZYLOTTO")
    print("=" * 50)
    
    # Vérifier la connexion DB
    try:
        from app.database.connection import engine, Base
        
        # Créer les tables si nécessaire
        Base.metadata.create_all(bind=engine)
        print("Base de donnees prete")
        
    except Exception as e:
        print(f"Erreur de connexion DB: {e}")
        return False
    
    # Générer les sessions de test
    if not create_test_sessions():
        return False
    
    # Générer les données d'analyse
    if not generate_analysis_data():
        print("Donnees d'analyse non generees (optionnel)")
    
    print("\nUTILISATION:")
    print("- Ouvrez l'application EazzyLotto")
    print("- Les sessions de test sont disponibles")
    print("- Testez les analyses et prédictions")
    print("- Explorez les différents univers")
    
    return True

if __name__ == "__main__":
    main()