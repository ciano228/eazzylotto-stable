#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost', database='katooling_main_system',
        user='postgres', password='Katulaa_33', port=5432
    )
    cursor = conn.cursor()
    
    # Test direct d'insertion
    session_id = 1
    draw_number = 1
    numbers = [12, 34, 56, 78, 90]
    
    print(f"Test insertion directe: Session {session_id}, Tirage #{draw_number}")
    
    # Supprimer s'il existe
    cursor.execute("DELETE FROM session_draws WHERE session_id = %s AND draw_number = %s", 
                   (session_id, draw_number))
    
    # Insérer
    import json
    cursor.execute("""
        INSERT INTO session_draws (
            session_id, draw_number, lottery_name, draw_date,
            winning_numbers, is_completed, is_no_draw
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        session_id, draw_number, 'Test Loto', '2025-01-01',
        json.dumps(numbers), True, False
    ))
    
    conn.commit()
    
    # Vérifier
    cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
    count = cursor.fetchone()[0]
    
    print(f"✅ Insertion réussie! Tirages en base: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")