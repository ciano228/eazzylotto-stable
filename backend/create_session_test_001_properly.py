#!/usr/bin/env python3
"""
Créer session_test_001 correctement dans katooling_main_system
"""

import psycopg2
import json
from datetime import datetime, timedelta
import random

def create_session_test_001_properly():
    """Créer session_test_001 avec la structure correcte de katooling_main_system"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33'
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Créer la session dans work_sessions
        # Vérifier si la session existe déjà
        cursor.execute("SELECT id FROM work_sessions WHERE name = %s", ('session_test_001',))
        existing = cursor.fetchone()
        
        if existing:
            session_id = existing[0]
            print(f"Session existante trouvée avec ID: {session_id}")
        else:
            cursor.execute("""
                INSERT INTO work_sessions (
                    name, description, lottery_type, numbers_per_draw,
                    number_range_min, number_range_max, total_draws,
                    current_draw, is_active, created_at, start_date,
                    cycle_length, lottery_schedule
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
            'session_test_001',
            'Session de test avec 42 tirages sur 6 périodes hebdomadaires',
            'Loto Test Hebdomadaire',
            5,  # numbers_per_draw
            1,  # number_range_min
            90, # number_range_max
            42, # total_draws (6 périodes × 7 jours)
            43, # current_draw (session complète)
            True, # is_active
            datetime.now(),
            datetime(2024, 10, 1), # start_date (mardi)
            7,  # cycle_length (hebdomadaire)
            json.dumps({
                'lundi': 'loto_lundi',
                'mardi': 'loto_mardi',
                'mercredi': 'loto_mercredi',
                'jeudi': 'loto_jeudi',
                'vendredi': 'loto_vendredi',
                'samedi': 'loto_samedi',
                'dimanche': 'loto_dimanche'
            })
        ))
        
            session_id = cursor.fetchone()[0]
            print(f"Session créée avec ID: {session_id}")
        
        # 2. Supprimer les anciens tirages
        cursor.execute("DELETE FROM session_draws WHERE session_id = %s", (session_id,))
        
        # 3. Créer les 42 tirages
        start_date = datetime(2024, 10, 1)  # Mardi
        loto_names = ['loto_lundi', 'loto_mardi', 'loto_mercredi', 'loto_jeudi', 'loto_vendredi', 'loto_samedi', 'loto_dimanche']
        
        for period in range(1, 7):  # 6 périodes
            for day in range(7):   # 7 jours par période
                draw_number = (period - 1) * 7 + day + 1
                draw_date = start_date + timedelta(days=(period - 1) * 7 + day)
                day_of_week = draw_date.weekday()  # 0=lundi, 6=dimanche
                lottery_name = loto_names[day_of_week]
                
                # Générer des numéros cohérents
                seed = int(draw_date.strftime('%Y%m%d'))
                random.seed(seed)
                numbers = sorted(random.sample(range(1, 91), 5))
                
                cursor.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_name, draw_date,
                        winning_numbers, is_completed, created_at, cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    draw_number,
                    lottery_name,
                    draw_date,
                    json.dumps(numbers),
                    True,  # Tous complétés
                    datetime.now(),
                    day + 1  # Position dans le cycle (1-7)
                ))
        
        conn.commit()
        print(f"42 tirages créés pour session_test_001")
        
        # 4. Vérification
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN is_completed THEN 1 END) as completed
            FROM session_draws WHERE session_id = %s
        """, (session_id,))
        
        counts = cursor.fetchone()
        print(f"Vérification: {counts[1]}/{counts[0]} tirages complétés")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    print("Création de session_test_001 dans katooling_main_system...")
    
    success = create_session_test_001_properly()
    
    if success:
        print("session_test_001 créée avec succès dans katooling_main_system")
        print("Accessible via les routes /api/katooling/*")
    else:
        print("Échec de la création")