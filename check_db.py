#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='katooling_main_system', 
        user='postgres',
        password='Katulaa_33',
        port=5432
    )
    cursor = conn.cursor()
    
    print("=== VÉRIFICATION BASE DE DONNÉES ===")
    
    # Vérifier session_draws
    cursor.execute("SELECT COUNT(*) FROM session_draws")
    count_draws = cursor.fetchone()[0]
    print(f"Nombre de tirages dans session_draws: {count_draws}")
    
    if count_draws > 0:
        cursor.execute("SELECT session_id, draw_number, lottery_name, winning_numbers, is_completed FROM session_draws ORDER BY session_id, draw_number LIMIT 5")
        draws = cursor.fetchall()
        print("\nPremiers tirages:")
        for draw in draws:
            print(f"  Session {draw[0]}, Tirage #{draw[1]}: {draw[2]} - {draw[3]} (Complété: {draw[4]})")
    
    # Vérifier work_sessions
    cursor.execute("SELECT COUNT(*) FROM work_sessions")
    count_sessions = cursor.fetchone()[0]
    print(f"\nNombre de sessions dans work_sessions: {count_sessions}")
    
    if count_sessions > 0:
        cursor.execute("SELECT id, name, total_draws, numbers_per_draw FROM work_sessions")
        sessions = cursor.fetchall()
        print("\nSessions:")
        for session in sessions:
            print(f"  ID {session[0]}: {session[1]} ({session[3]} numéros, {session[2]} tirages)")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}")