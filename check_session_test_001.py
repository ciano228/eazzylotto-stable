import psycopg2

def check_session_test_001():
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33'
        )
        
        # Création d'un curseur
        cur = conn.cursor()
        
        # Vérification de la session_test_001
        print("Vérification de la session 'session_test_001'...")
        
        # Recherche de la session par nom
        cur.execute("""
            SELECT * FROM unified_sessions 
            WHERE name = 'session_test_001' 
            OR session_uuid = 'session_test_001'
        """)
        
        session = cur.fetchone()
        
        if session:
            print("\nSession trouvée :")
            print(f"- ID: {session[0]}")
            print(f"- UUID: {session[1]}")
            print(f"- Nom: {session[2]}")
            print(f"- Description: {session[3]}")
            print(f"- Tirages totaux: {session[4]}")
            print(f"- Créée le: {session[5]}")
            print(f"- Active: {session[6]}")
            
            # Vérification des tirages pour cette session
            cur.execute("""
                SELECT * FROM unified_draws 
                WHERE session_uuid = %s
                ORDER BY draw_number
                LIMIT 5
            """, (session[0],))
            
            draws = cur.fetchall()
            print(f"\n{len(draws)} premiers tirages trouvés :")
            for draw in draws:
                print(f"- Tirage {draw[2]}: {draw[3]} - Numéros: {draw[4]}")
        else:
            print("\nLa session 'session_test_001' n'a pas été trouvée dans la base de données.")
            
            # Vérification des noms de sessions similaires
            cur.execute("""
                SELECT name, session_uuid, created_at 
                FROM unified_sessions 
                WHERE name LIKE '%test%' OR name LIKE '%session%'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            similar_sessions = cur.fetchall()
            if similar_sessions:
                print("\nSessions similaires trouvées :")
                for s in similar_sessions:
                    print(f"- {s[0]} (UUID: {s[1]}, Créée le: {s[2]})")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la vérification de la session: {e}")

if __name__ == "__main__":
    check_session_test_001()
