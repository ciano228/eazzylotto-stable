#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour verifier les informations de la session 'test session'
"""
import psycopg2
from datetime import datetime
import json
import sys
import io

# Forcer l'encodage UTF-8 pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration BD
db_config = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def test_session_info():
    """Teste les informations de la session 'test session'"""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("RECHERCHE DE LA SESSION 'test session'")
        print("=" * 80)
        
        # Rechercher la session
        cursor.execute("""
            SELECT id, name, lottery_type, numbers_per_draw, total_draws, 
                   lottery_schedule, start_date, is_active
            FROM work_sessions
            WHERE LOWER(name) LIKE '%test%'
            ORDER BY id DESC
        """)
        
        sessions = cursor.fetchall()
        
        if not sessions:
            print("ERREUR: Aucune session 'test' trouvee dans la base de donnees")
            print("\nSessions disponibles:")
            cursor.execute("SELECT id, name FROM work_sessions ORDER BY id DESC LIMIT 10")
            all_sessions = cursor.fetchall()
            for s in all_sessions:
                print(f"   - ID {s[0]}: {s[1]}")
            return
        
        print(f"\nSUCCES: {len(sessions)} session(s) trouvee(s):\n")
        
        for session in sessions:
            session_id, name, lottery_type, numbers_per_draw, total_draws, schedule, start_date, is_active = session
            end_date = None  # Pas de colonne end_date dans la table
            
            print(f"SESSION: {name}")
            print(f"   ID: {session_id}")
            print(f"   Type de loterie: {lottery_type}")
            print(f"   Numeros par tirage: {numbers_per_draw}")
            print(f"   Total tirages prevus: {total_draws}")
            print(f"   Statut: {'ACTIVE' if is_active else 'INACTIVE'}")
            
            # Planning
            if schedule:
                try:
                    schedule_data = json.loads(schedule) if isinstance(schedule, str) else schedule
                    periodicite = len(schedule_data)
                    print(f"   Periodicite: {periodicite} tirages/periode")
                    print(f"   Planning: {', '.join([s['name'] for s in schedule_data])}")
                except:
                    print(f"   Planning: {schedule}")
            else:
                print("   Planning: Non defini")
            
            # Dates de session
            print(f"   Date debut session: {start_date if start_date else 'Non definie'}")
            print(f"   Date fin session: Calculee depuis les tirages")
            
            # Recuperer les tirages
            cursor.execute("""
                SELECT draw_number, draw_date, lottery_name, winning_numbers, is_completed
                FROM session_draws
                WHERE session_id = %s
                ORDER BY draw_date
            """, (session_id,))
            
            draws = cursor.fetchall()
            
            print(f"\n   TIRAGES ENREGISTRES: {len(draws)}")
            
            if draws:
                # Dates min/max des tirages
                dates = [d[1] for d in draws if d[1]]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    print(f"   Periode des tirages: {min_date} -> {max_date}")
                    
                    # Calculer les periodes
                    periodicite = len(schedule_data) if schedule and schedule_data else 3
                    total_periods = (len(draws) + periodicite - 1) // periodicite
                    print(f"   Periode de travail: P1 -> P{total_periods} ({total_periods} periodes)")
                
                print(f"\n   Detail des tirages:")
                for draw in draws[:10]:  # Afficher max 10 tirages
                    draw_num, draw_date, lottery_name, numbers, completed = draw
                    numbers_str = ', '.join(map(str, numbers)) if numbers else 'Aucun'
                    status = 'OK' if completed else 'EN COURS'
                    print(f"      [{status}] Tirage #{draw_num} - {draw_date} - {lottery_name}: [{numbers_str}]")
                
                if len(draws) > 10:
                    print(f"      ... et {len(draws) - 10} autres tirages")
            else:
                print("   ATTENTION: Aucun tirage enregistre pour cette session")
            
            print("\n" + "=" * 80 + "\n")
        
        cursor.close()
        conn.close()
        
        print("\nTest termine avec succes!")
        
    except Exception as e:
        print(f"\nERREUR lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_info()
