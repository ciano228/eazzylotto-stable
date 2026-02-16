#!/usr/bin/env python3
"""
Correctif pour se connecter à la vraie base de données katooling_main_system
"""

import psycopg2
import json

def connect_to_katooling():
    """Se connecter à la base katooling_main_system"""
    
    # Configurations de connexion à tester
    db_configs = [
        {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': 'Katulaa_33'},
        {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': 'Katula2024'},
        {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': 'postgres'},
    ]
    
    conn = None
    working_config = None
    
    for config in db_configs:
        try:
            conn = psycopg2.connect(**config)
            working_config = config
            print(f"Connexion reussie a katooling_main_system avec mot de passe: {config['password']}")
            break
        except Exception as e:
            print(f"Echec avec {config['password']}: {e}")
            continue
    
    if not conn:
        print("Impossible de se connecter a katooling_main_system")
        return None, None
    
    return conn, working_config

def explore_katooling_database():
    """Explorer la structure de katooling_main_system"""
    
    conn, config = connect_to_katooling()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 1. Lister toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"\nTables disponibles dans katooling_main_system:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 2. Chercher les tables liées aux sessions
        session_tables = [t[0] for t in tables if 'session' in t[0].lower()]
        if session_tables:
            print(f"\nTables de sessions trouvees:")
            for table in session_tables:
                print(f"  - {table}")
                
                # Compter les enregistrements
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    Enregistrements: {count}")
                    
                    # Afficher quelques colonnes
                    cursor.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' 
                        ORDER BY ordinal_position
                        LIMIT 10
                    """)
                    columns = cursor.fetchall()
                    print(f"    Colonnes: {', '.join([f'{col[0]}({col[1]})' for col in columns])}")
                    
                except Exception as e:
                    print(f"    Erreur lecture {table}: {e}")
        
        # 3. Chercher les tables liées aux tirages/draws
        draw_tables = [t[0] for t in tables if any(keyword in t[0].lower() for keyword in ['draw', 'tirage', 'loto', 'game'])]
        if draw_tables:
            print(f"\nTables de tirages trouvees:")
            for table in draw_tables:
                print(f"  - {table}")
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    Enregistrements: {count}")
                except Exception as e:
                    print(f"    Erreur: {e}")
        
        # 4. Chercher Algeria spécifiquement
        print(f"\nRecherche de donnees Algeria...")
        for table in [t[0] for t in tables]:
            try:
                # Chercher dans les noms/descriptions
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    AND (column_name ILIKE '%name%' OR column_name ILIKE '%description%' OR column_name ILIKE '%title%')
                """)
                name_columns = cursor.fetchall()
                
                for col in name_columns:
                    col_name = col[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col_name} ILIKE '%algeria%'")
                    algeria_count = cursor.fetchone()[0]
                    
                    if algeria_count > 0:
                        print(f"  Algeria trouvee dans {table}.{col_name}: {algeria_count} enregistrements")
                        
                        # Afficher quelques exemples
                        cursor.execute(f"SELECT {col_name} FROM {table} WHERE {col_name} ILIKE '%algeria%' LIMIT 3")
                        examples = cursor.fetchall()
                        for example in examples:
                            print(f"    Exemple: {example[0]}")
                            
            except Exception as e:
                continue
        
        # 5. Sauvegarder la configuration qui fonctionne
        save_working_config(config)
        
        cursor.close()
        conn.close()
        
        return config
        
    except Exception as e:
        print(f"Erreur exploration: {e}")
        cursor.close()
        conn.close()
        return None

def save_working_config(config):
    """Sauvegarder la configuration qui fonctionne"""
    try:
        config_data = {
            'database': 'katooling_main_system',
            'host': config['host'],
            'user': config['user'],
            'password': config['password'],
            'port': config.get('port', 5432)
        }
        
        with open('katooling_db_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"\nConfiguration sauvegardee dans katooling_db_config.json")
        
    except Exception as e:
        print(f"Erreur sauvegarde config: {e}")

def test_algeria_access():
    """Tester l'accès spécifique aux données Algeria"""
    
    conn, config = connect_to_katooling()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Chercher toutes les références à Algeria
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        algeria_data = {}
        
        for table in tables:
            table_name = table[0]
            try:
                # Chercher les colonnes texte
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    AND data_type IN ('text', 'character varying', 'varchar')
                """)
                text_columns = cursor.fetchall()
                
                for col in text_columns:
                    col_name = col[0]
                    cursor.execute(f"""
                        SELECT COUNT(*), {col_name}
                        FROM {table_name} 
                        WHERE {col_name} ILIKE '%algeria%'
                        GROUP BY {col_name}
                        LIMIT 5
                    """)
                    results = cursor.fetchall()
                    
                    if results:
                        if table_name not in algeria_data:
                            algeria_data[table_name] = {}
                        algeria_data[table_name][col_name] = results
                        
            except Exception as e:
                continue
        
        if algeria_data:
            print(f"\nDonnees Algeria trouvees:")
            for table, columns in algeria_data.items():
                print(f"\nTable: {table}")
                for col, data in columns.items():
                    print(f"  Colonne {col}:")
                    for count, value in data:
                        print(f"    {count}x: {value}")
        else:
            print("\nAucune donnee Algeria trouvee")
        
        cursor.close()
        conn.close()
        
        return algeria_data
        
    except Exception as e:
        print(f"Erreur test Algeria: {e}")
        cursor.close()
        conn.close()
        return {}

if __name__ == "__main__":
    print("Connexion a la base katooling_main_system...")
    
    # 1. Explorer la structure
    config = explore_katooling_database()
    
    if config:
        print(f"\n" + "="*50)
        print("CONFIGURATION FONCTIONNELLE:")
        print(f"Database: katooling_main_system")
        print(f"Host: {config['host']}")
        print(f"User: {config['user']}")
        print(f"Password: {config['password']}")
        print("="*50)
        
        # 2. Tester l'accès Algeria
        print(f"\nTest acces Algeria...")
        algeria_data = test_algeria_access()
        
        if algeria_data:
            print(f"\nAlgeria accessible dans katooling_main_system!")
        else:
            print(f"\nAlgeria non trouve - verifiez les noms de tables/colonnes")
    else:
        print("Echec connexion a katooling_main_system")