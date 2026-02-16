"""
Script de test de connexion à la base de données
"""

def test_db_connection():
    import psycopg2
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    try:
        print("Tentative de connexion à la base de données...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Vérifier les tables existantes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        print("\nTables disponibles dans la base de données:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Vérifier les sessions unifiées
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        session_count = cursor.fetchone()[0]
        print(f"\nNombre de sessions unifiées: {session_count}")
        
        if session_count > 0:
            cursor.execute("SELECT session_uuid, name, created_at FROM unified_sessions ORDER BY created_at DESC LIMIT 5")
            print("\nDernières sessions:")
            for session in cursor.fetchall():
                print(f"- {session[1]} (ID: {session[0]}, Créée le: {session[2]})")
        
        cursor.close()
        conn.close()
        print("\nConnexion à la base de données réussie!")
        
    except Exception as e:
        print(f"\nERREUR: Impossible de se connecter à la base de données")
        print(f"Détails: {str(e)}")
        print("\nVérifiez que:")
        print("1. PostgreSQL est bien installé et en cours d'exécution")
        print("2. La base de données 'katooling_main_system' existe")
        print("3. Les identifiants de connexion sont corrects")
        print("4. L'utilisateur a les droits nécessaires")

if __name__ == "__main__":
    test_db_connection()
