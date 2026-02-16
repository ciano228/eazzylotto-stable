#!/usr/bin/env python3
"""
Script d'analyse complète de la base de données PostgreSQL
Recherche toutes les sessions et tirages avec différents noms possibles
"""

import psycopg2
import json
from typing import Dict, List, Any

def analyze_database():
    """Analyse complète de toutes les bases PostgreSQL"""
    
    # Configurations possibles
    configs = [
        {
            'name': 'katula_db (admin123)',
            'host': 'localhost',
            'database': 'katula_db',
            'user': 'postgres',
            'password': 'admin123',
            'port': 5432
        },
        {
            'name': 'katooling_main_system (Katula2024)',
            'host': 'localhost', 
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katula2024',
            'port': 5432
        },
        {
            'name': 'postgres (admin123)',
            'host': 'localhost',
            'database': 'postgres', 
            'user': 'postgres',
            'password': 'admin123',
            'port': 5432
        }
    ]
    
    # Mots-clés pour identifier les tables de sessions/tirages
    session_keywords = ['session', 'work', 'projet', 'analysis']
    draw_keywords = ['draw', 'tirage', 'tirrage', 'resultat', 'loto', 'lottery', 'result', 'numero', 'number']
    
    results = {}
    
    for config in configs:
        print(f"\n{'='*60}")
        print(f"🔍 ANALYSE: {config['name']}")
        print(f"{'='*60}")
        
        try:
            conn = psycopg2.connect(
                host=config['host'],
                database=config['database'], 
                user=config['user'],
                password=config['password'],
                port=config['port']
            )
            cursor = conn.cursor()
            
            print(f"✅ Connexion réussie à {config['database']}")
            
            # Lister toutes les tables
            cursor.execute("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            all_tables = cursor.fetchall()
            print(f"📊 Total tables: {len(all_tables)}")
            
            # Analyser les tables par catégorie
            session_tables = []
            draw_tables = []
            other_tables = []
            
            for table_name, table_type in all_tables:
                table_lower = table_name.lower()
                
                # Vérifier si c'est une table de sessions
                if any(keyword in table_lower for keyword in session_keywords):
                    session_tables.append(table_name)
                # Vérifier si c'est une table de tirages
                elif any(keyword in table_lower for keyword in draw_keywords):
                    draw_tables.append(table_name)
                else:
                    other_tables.append(table_name)
            
            # Analyser les tables de sessions
            if session_tables:
                print(f"\n🎯 TABLES DE SESSIONS ({len(session_tables)}):")
                for table in session_tables:
                    analyze_table(cursor, table, 'session')
            
            # Analyser les tables de tirages
            if draw_tables:
                print(f"\n🎲 TABLES DE TIRAGES ({len(draw_tables)}):")
                for table in draw_tables:
                    analyze_table(cursor, table, 'draw')
            
            # Chercher dans les autres tables des colonnes suspectes
            print(f"\n🔍 RECHERCHE DANS AUTRES TABLES ({len(other_tables)}):")
            suspicious_tables = []
            
            for table in other_tables[:20]:  # Limiter pour éviter trop de requêtes
                try:
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                    """)
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    # Chercher des colonnes suspectes
                    suspicious_columns = []
                    for col in columns:
                        col_lower = col.lower()
                        if any(keyword in col_lower for keyword in session_keywords + draw_keywords):
                            suspicious_columns.append(col)
                    
                    if suspicious_columns:
                        suspicious_tables.append((table, suspicious_columns))
                        
                except Exception as e:
                    continue
            
            if suspicious_tables:
                print("  Tables avec colonnes suspectes:")
                for table, columns in suspicious_tables:
                    print(f"    📋 {table}: {columns}")
                    analyze_table(cursor, table, 'suspicious')
            else:
                print("  Aucune table suspecte trouvée")
            
            # Sauvegarder les résultats
            results[config['name']] = {
                'status': 'success',
                'total_tables': len(all_tables),
                'session_tables': session_tables,
                'draw_tables': draw_tables,
                'suspicious_tables': [t[0] for t, c in suspicious_tables]
            }
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur connexion {config['name']}: {e}")
            results[config['name']] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📋 RÉSUMÉ FINAL")
    print(f"{'='*60}")
    
    for db_name, result in results.items():
        if result['status'] == 'success':
            print(f"\n✅ {db_name}:")
            print(f"  - Tables sessions: {len(result['session_tables'])}")
            print(f"  - Tables tirages: {len(result['draw_tables'])}")
            print(f"  - Tables suspectes: {len(result['suspicious_tables'])}")
            
            if result['session_tables']:
                print(f"    Sessions: {result['session_tables']}")
            if result['draw_tables']:
                print(f"    Tirages: {result['draw_tables']}")
        else:
            print(f"\n❌ {db_name}: {result['error']}")
    
    return results

def analyze_table(cursor, table_name: str, table_type: str):
    """Analyse détaillée d'une table"""
    try:
        # Compter les enregistrements
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # Récupérer les colonnes
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"  📊 {table_name}: {count} enregistrements")
        print(f"    Colonnes: {[f'{col[0]}({col[1]})' for col in columns[:5]]}")
        
        if count > 0 and count <= 10:
            # Afficher quelques exemples si peu d'enregistrements
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            for i, row in enumerate(rows):
                print(f"    Exemple {i+1}: {dict(zip(column_names[:3], row[:3]))}")
        
        elif count > 0:
            # Afficher juste les premières colonnes pour les grandes tables
            first_cols = [col[0] for col in columns[:3]]
            cursor.execute(f"SELECT {', '.join(first_cols)} FROM {table_name} LIMIT 2")
            rows = cursor.fetchall()
            
            for i, row in enumerate(rows):
                print(f"    Exemple {i+1}: {dict(zip(first_cols, row))}")
        
    except Exception as e:
        print(f"  {table_name}: Erreur - {e}")

if __name__ == "__main__":
    analyze_database()