#!/usr/bin/env python3
"""
Script pour vérifier et configurer la connexion à la base de données
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_postgresql_connection():
    """Teste la connexion PostgreSQL"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Test de connexion à: {DATABASE_URL}")
        
        # Extraire les paramètres de connexion
        if DATABASE_URL.startswith("postgresql://"):
            # Format: postgresql://user:password@host:port/database
            parts = DATABASE_URL.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            host_port = host_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1]
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            database = host_db[1]
            
            print(f"Connexion à PostgreSQL:")
            print(f"  Host: {host}:{port}")
            print(f"  Database: {database}")
            print(f"  User: {user}")
            
            # Test de connexion
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connexion reussie!")
            print(f"   Version PostgreSQL: {version[0]}")
            
            # Vérifier les tables existantes
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   Tables trouvées: {len(tables)}")
            for table in tables[:10]:  # Afficher les 10 premières
                print(f"     - {table[0]}")
            if len(tables) > 10:
                print(f"     ... et {len(tables) - 10} autres")
            
            cursor.close()
            conn.close()
            return True
            
    except Exception as e:
        print(f"Erreur de connexion PostgreSQL: {e}")
        return False

def create_sqlite_fallback():
    """Crée une configuration SQLite de secours"""
    print("\nConfiguration SQLite de secours...")
    
    sqlite_url = "sqlite:///./katooling_main_system.db"
    
    # Créer le fichier .env.sqlite
    with open(".env.sqlite", "w") as f:
        f.write(f"DATABASE_URL={sqlite_url}\n")
        f.write("CORS_ORIGINS=http://localhost:8081,http://localhost:3000,http://localhost:8080\n")
        f.write("DEBUG=True\n")
        f.write("SECRET_KEY=your-secret-key-here\n")
        f.write("JWT_SECRET_KEY=your-jwt-secret-key-here\n")
    
    print(f"Configuration SQLite creee: {sqlite_url}")
    print("   Fichier: .env.sqlite")
    
    return sqlite_url

def main():
    print("Verification de la base de donnees...")
    
    # Test PostgreSQL
    if test_postgresql_connection():
        print("\nPostgreSQL fonctionne - Aucune action necessaire")
    else:
        print("\nPostgreSQL non accessible")
        
        # Proposer SQLite comme alternative
        response = input("Voulez-vous utiliser SQLite comme alternative? (y/n): ")
        if response.lower() in ['y', 'yes', 'o', 'oui']:
            sqlite_url = create_sqlite_fallback()
            print(f"\nPour utiliser SQLite, renommez:")
            print(f"   .env -> .env.postgresql")
            print(f"   .env.sqlite -> .env")
            print(f"\nPuis relancez l'application.")
        else:
            print("\nSolutions pour PostgreSQL:")
            print("1. Verifiez que PostgreSQL est demarre")
            print("2. Verifiez les parametres de connexion dans .env")
            print("3. Creez la base de donnees 'katooling_main_system'")

if __name__ == "__main__":
    main()