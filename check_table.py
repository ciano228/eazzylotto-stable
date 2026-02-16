#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost', database='katooling_main_system',
        user='postgres', password='Katulaa_33', port=5432
    )
    cursor = conn.cursor()
    
    print("=== STRUCTURE TABLE session_draws ===")
    
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'session_draws'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}")