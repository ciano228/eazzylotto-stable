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
    
    # Lister les tables
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables disponibles:", tables)
    
    # Vérifier table_de_katula
    if 'table_de_katula' in tables:
        cursor.execute('SELECT COUNT(*) FROM table_de_katula')
        count = cursor.fetchone()[0]
        print(f'Lignes dans table_de_katula: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM table_de_katula LIMIT 3')
            rows = cursor.fetchall()
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'table_de_katula' ORDER BY ordinal_position")
            columns = [row[0] for row in cursor.fetchall()]
            print('Colonnes:', columns)
            for row in rows:
                print('Échantillon:', row)
    else:
        print("Table table_de_katula n'existe pas")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Erreur connexion DB: {e}')