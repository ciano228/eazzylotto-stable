import psycopg2

def check_unified_sessions():
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        
        # Création d'un curseur
        cur = conn.cursor()
        
        # Vérification de la structure de la table
        print("=== Structure de la table unified_sessions ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'unified_sessions'
            ORDER BY ordinal_position
        """)
        
        print("\nColonnes de la table unified_sessions :")
        print("-" * 80)
        print(f"{'Nom':<25} | {'Type':<20} | Nullable | Valeur par défaut")
        print("-" * 80)
        
        for col in cur.fetchall():
            print(f"{col[0]:<25} | {col[1]:<20} | {col[2]:<8} | {col[3]}")
        
        # Vérification du contenu de la table
        print("\n\n=== Contenu de la table unified_sessions ===")
        cur.execute("""
            SELECT * FROM unified_sessions 
            WHERE name = 'session_test_001' 
            OR name LIKE '%test%' 
            ORDER BY created_at DESC
        """)
        
        sessions = cur.fetchall()
        print(f"\n{sessions} sessions de test trouvées :")
        
        if sessions:
            print("\nDétails des sessions de test :")
            print("-" * 100)
            for i, session in enumerate(sessions, 1):
                print(f"\nSession {i}:")
                for j, value in enumerate(session):
                    col_name = cur.description[j].name if cur.description else f"Colonne {j+1}"
                    print(f"- {col_name}: {value}")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la vérification de la table unified_sessions: {e}")

if __name__ == "__main__":
    check_unified_sessions()
