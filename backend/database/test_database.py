#!/usr/bin/env python3
"""
Test complet de la connexion à la base de données PostgreSQL
"""

import os
import sys
from dotenv import load_dotenv
import traceback

def test_env_variables():
    """Test des variables d'environnement"""
    print("=== TEST DES VARIABLES D'ENVIRONNEMENT ===")
    
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"[OK] DATABASE_URL trouvée: {db_url}")
        
        # Analyser l'URL
        if 'postgresql://' in db_url:
            parts = db_url.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_db = parts[1].split('/')
                
                print(f"[INFO] Utilisateur: {user_pass[0]}")
                print(f"[INFO] Host: {host_db[0].split(':')[0]}")
                print(f"[INFO] Port: {host_db[0].split(':')[1] if ':' in host_db[0] else '5432'}")
                print(f"[INFO] Base: {host_db[1] if len(host_db) > 1 else 'N/A'}")
        
        return True
    else:
        print("[ERROR] DATABASE_URL non trouvée dans .env")
        return False

def test_psycopg2():
    """Test du driver PostgreSQL"""
    print("\n=== TEST DU DRIVER POSTGRESQL ===")
    
    try:
        import psycopg2
        print(f"[OK] psycopg2 version: {psycopg2.__version__}")
        return True
    except ImportError as e:
        print(f"[ERROR] psycopg2 non installé: {e}")
        return False

def test_sqlalchemy():
    """Test de SQLAlchemy"""
    print("\n=== TEST DE SQLALCHEMY ===")
    
    try:
        import sqlalchemy
        print(f"[OK] SQLAlchemy version: {sqlalchemy.__version__}")
        return True
    except ImportError as e:
        print(f"[ERROR] SQLAlchemy non installé: {e}")
        return False

def test_database_connection():
    """Test de connexion directe à PostgreSQL"""
    print("\n=== TEST DE CONNEXION DIRECTE ===")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            print("[ERROR] DATABASE_URL manquante")
            return False
        
        # Extraire les paramètres de connexion
        # postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system
        db_url = db_url.replace('postgresql://', '')
        user_pass, host_db = db_url.split('@')
        user, password = user_pass.split(':')
        host_port, database = host_db.split('/')
        host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
        
        # Tentative de connexion
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("[OK] Connexion PostgreSQL réussie")
        
        # Test d'une requête simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[OK] Version PostgreSQL: {version[0]}")
        
        # Test des tables existantes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"[INFO] Tables trouvées: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Connexion échouée: {e}")
        traceback.print_exc()
        return False

def test_sqlalchemy_connection():
    """Test de connexion via SQLAlchemy"""
    print("\n=== TEST DE CONNEXION SQLALCHEMY ===")
    
    try:
        from app.database.connection import engine, Base
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            test_value = result.fetchone()
            print(f"[OK] Connexion SQLAlchemy réussie: {test_value}")
        
        # Test des métadonnées
        print(f"[INFO] Tables définies dans Base.metadata: {len(Base.metadata.tables)}")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] SQLAlchemy connexion échouée: {e}")
        traceback.print_exc()
        return False

def test_database_creation():
    """Test de création des tables"""
    print("\n=== TEST DE CRÉATION DES TABLES ===")
    
    try:
        from app.database.connection import engine, Base
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables créées avec succès")
        
        # Vérifier les tables créées
        with engine.connect() as conn:
            result = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = result.fetchall()
            
            print(f"[INFO] Tables présentes après création: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Création tables échouée: {e}")
        traceback.print_exc()
        return False

def main():
    print("TEST COMPLET DE LA BASE DE DONNÉES POSTGRESQL")
    print("=" * 60)
    
    tests = [
        ("Variables d'environnement", test_env_variables),
        ("Driver psycopg2", test_psycopg2),
        ("SQLAlchemy", test_sqlalchemy),
        ("Connexion directe PostgreSQL", test_database_connection),
        ("Connexion SQLAlchemy", test_sqlalchemy_connection),
        ("Création des tables", test_database_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FATAL] Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "[OK]" if success else "[ERREUR]"
        print(f"{status} {test_name}")
        if success:
            success_count += 1
    
    print(f"\nTests réussis: {success_count}/{len(tests)}")
    
    if success_count == len(tests):
        print("\n🎉 TOUTES LES CONNEXIONS FONCTIONNENT PARFAITEMENT!")
        print("✅ PostgreSQL est opérationnel")
        print("✅ SQLAlchemy configuré correctement")
        print("✅ Tables créées avec succès")
    else:
        print(f"\n⚠️ {len(tests) - success_count} problème(s) détecté(s)")
        print("Consultez les détails ci-dessus pour résoudre les problèmes")
    
    return success_count == len(tests)

if __name__ == "__main__":
    main()
