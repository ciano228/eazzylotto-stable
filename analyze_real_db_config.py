#!/usr/bin/env python3
"""
Analyser les vraies configurations PostgreSQL utilisées par l'application
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def analyze_db_configs():
    """Analyser toutes les configurations PostgreSQL dans le code"""
    
    print("=== ANALYSE DES CONFIGURATIONS POSTGRESQL ===\n")
    
    # 1. Configuration du KatulaCompleteService
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        config = service.db_config
        print("1. KatulaCompleteService:")
        print(f"   Host: {config['host']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        print(f"   Password: {config['password'][:3]}***")
        print(f"   Port: {config['port']}")
        
        # Tester la connexion
        try:
            import psycopg2
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Lister les tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [t[0] for t in cursor.fetchall()]
            print(f"   Status: CONNEXION REUSSIE")
            print(f"   Tables ({len(tables)}): {tables[:10]}{'...' if len(tables) > 10 else ''}")
            
            # Chercher tables de sessions/tirages
            session_tables = [t for t in tables if any(k in t.lower() for k in ['session', 'work', 'projet'])]
            draw_tables = [t for t in tables if any(k in t.lower() for k in ['draw', 'tirage', 'resultat', 'loto', 'lottery'])]
            
            if session_tables:
                print(f"   SESSIONS TROUVEES: {session_tables}")
                for table in session_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table}: {count} enregistrements")
                    
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                        rows = cursor.fetchall()
                        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
                        columns = [col[0] for col in cursor.fetchall()]
                        
                        for i, row in enumerate(rows):
                            sample = dict(zip(columns[:3], row[:3]))
                            print(f"       Exemple {i+1}: {sample}")
            
            if draw_tables:
                print(f"   TIRAGES TROUVES: {draw_tables}")
                for table in draw_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table}: {count} enregistrements")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   Status: ERREUR CONNEXION - {e}")
        
    except Exception as e:
        print(f"1. KatulaCompleteService: ERREUR - {e}")
    
    print()
    
    # 2. Configuration du MigrationService
    try:
        from backend.migration_service import MigrationService
        service = MigrationService()
        config = service.db_config
        print("2. MigrationService:")
        print(f"   Host: {config['host']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        print(f"   Password: {config['password'][:3]}***")
        print(f"   Port: {config['port']}")
        
        # Tester la connexion
        try:
            import psycopg2
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Lister les tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [t[0] for t in cursor.fetchall()]
            print(f"   Status: CONNEXION REUSSIE")
            print(f"   Tables ({len(tables)}): {tables[:10]}{'...' if len(tables) > 10 else ''}")
            
            # Chercher tables de sessions/tirages
            session_tables = [t for t in tables if any(k in t.lower() for k in ['session', 'work', 'projet'])]
            draw_tables = [t for t in tables if any(k in t.lower() for k in ['draw', 'tirage', 'resultat', 'loto', 'lottery'])]
            
            if session_tables:
                print(f"   SESSIONS TROUVEES: {session_tables}")
                for table in session_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table}: {count} enregistrements")
                    
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                        rows = cursor.fetchall()
                        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
                        columns = [col[0] for col in cursor.fetchall()]
                        
                        for i, row in enumerate(rows):
                            sample = dict(zip(columns[:3], row[:3]))
                            print(f"       Exemple {i+1}: {sample}")
            
            if draw_tables:
                print(f"   TIRAGES TROUVES: {draw_tables}")
                for table in draw_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table}: {count} enregistrements")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   Status: ERREUR CONNEXION - {e}")
        
    except Exception as e:
        print(f"2. MigrationService: ERREUR - {e}")
    
    print()
    
    # 3. Vérifier les fichiers .env
    print("3. Fichiers de configuration:")
    
    env_files = [
        'backend/.env',
        '.env',
        'frontend/.env'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   {env_file}: EXISTE")
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'DATABASE_URL' in content:
                        lines = [line for line in content.split('\n') if 'DATABASE_URL' in line]
                        for line in lines:
                            print(f"     {line}")
                    if 'POSTGRES' in content:
                        lines = [line for line in content.split('\n') if 'POSTGRES' in line]
                        for line in lines:
                            print(f"     {line}")
            except Exception as e:
                print(f"     Erreur lecture: {e}")
        else:
            print(f"   {env_file}: N'EXISTE PAS")
    
    print()
    
    # 4. Résumé et recommandations
    print("=== RESUME ET DIAGNOSTIC ===")
    print()
    print("PROBLEMES IDENTIFIES:")
    print("1. Configurations PostgreSQL multiples avec mots de passe différents")
    print("2. Bases de données différentes (katula_db vs katooling_main_system)")
    print("3. Authentification PostgreSQL échoue")
    print()
    print("SOLUTIONS:")
    print("1. Vérifier le mot de passe PostgreSQL réel")
    print("2. Créer les bases de données manquantes")
    print("3. Unifier les configurations")
    print("4. Vérifier que PostgreSQL accepte les connexions")

if __name__ == "__main__":
    analyze_db_configs()