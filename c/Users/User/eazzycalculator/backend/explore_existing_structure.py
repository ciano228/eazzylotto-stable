#!/usr/bin/env python3
"""
Exploration complète de la structure existante
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def explore_complete_structure():
    """Explorer toute la structure existante"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        
        cursor = conn.cursor()
        
        print("=== EXPLORATION STRUCTURE COMPLETE ===\n")
        
        # 1. Toutes les tables
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as col_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        all_tables = cursor.fetchall()
        
        print(f"TOTAL TABLES: {len(all_tables)}")
        for table_name, col_count in all_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  {table_name}: {row_count} lignes, {col_count} colonnes")
        
        # 2. Tables principales identifiées
        main_tables = [
            'table_de_katula', 'chips', 'chips_relation', 'work_sessions', 
            'session_draws', 'combinations', 'draws'
        ]
        
        print(f"\n=== TABLES PRINCIPALES ===")
        for table in main_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Structure
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                
                print(f"\n{table.upper()}: {count} lignes")
                print("  Colonnes:")
                for col_name, data_type, nullable in columns:
                    print(f"    - {col_name} ({data_type}) {'NULL' if nullable == 'YES' else 'NOT NULL'}")
                
                # Échantillon de données
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    samples = cursor.fetchall()
                    print("  Échantillons:")
                    for i, sample in enumerate(samples):
                        print(f"    Ligne {i+1}: {str(sample)[:100]}...")
                        
            except Exception as e:
                print(f"  {table}: ERREUR - {e}")
        
        # 3. Relations et clés étrangères
        print(f"\n=== RELATIONS ===")
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name
        """)
        relations = cursor.fetchall()
        
        for table, column, foreign_table, foreign_column in relations:
            print(f"  {table}.{column} -> {foreign_table}.{foreign_column}")
        
        # 4. Données par univers
        print(f"\n=== DONNEES PAR UNIVERS ===")
        
        # Table de Katula par univers
        cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
        universes_katula = [u[0] for u in cursor.fetchall()]
        
        for universe in universes_katula:
            cursor.execute("SELECT COUNT(*) FROM table_de_katula WHERE univers = %s", (universe,))
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT DISTINCT forme 
                FROM table_de_katula 
                WHERE univers = %s AND forme IS NOT NULL
                ORDER BY forme
            """, (universe,))
            formes = [f[0] for f in cursor.fetchall()]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT chip) 
                FROM table_de_katula 
                WHERE univers = %s
            """, (universe,))
            unique_chips = cursor.fetchone()[0]
            
            print(f"  {universe.upper()}: {count} entrées, {unique_chips} chips uniques")
            print(f"    Formes: {formes}")
        
        # 5. Vérifier les endpoints existants
        print(f"\n=== VERIFICATION ENDPOINTS EXISTANTS ===")
        
        # Chercher les fichiers de routes
        routes_dir = "app/routes"
        if os.path.exists(routes_dir):
            for file in os.listdir(routes_dir):
                if file.endswith('.py') and file != '__init__.py':
                    print(f"  Route file: {file}")
                    
                    # Lire le contenu pour voir les endpoints
                    with open(os.path.join(routes_dir, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extraire les endpoints
                    import re
                    endpoints = re.findall(r'@router\.(get|post|put|delete)\("([^"]+)"\)', content)
                    for method, path in endpoints:
                        print(f"    {method.upper()} {path}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    explore_complete_structure()