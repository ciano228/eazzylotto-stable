import psycopg2

def check_draws():
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
        
        # Vérification des tirages par session
        print("Vérification des tirages par session...")
        
        # Récupération du nombre de tirages par session
        cur.execute("""
            SELECT 
                s.session_uuid, 
                s.name as session_name,
                s.created_at,
                COUNT(d.draw_number) as nb_draws
            FROM 
                unified_sessions s
            LEFT JOIN 
                unified_draws d ON s.session_uuid = d.session_uuid
            GROUP BY 
                s.session_uuid, s.name, s.created_at
            ORDER BY 
                nb_draws DESC, s.created_at DESC
        """)
        
        print("\nRésumé des tirages par session :")
        print("-" * 80)
        print(f"{'ID de session':<40} | {'Nom de session':<30} | {'Nombre de tirages':<15}")
        print("-" * 80)
        
        sessions = cur.fetchall()
        for session in sessions:
            session_uuid = session[0] or 'NULL'
            session_name = session[1] or 'Inconnu'
            nb_draws = session[2] or 0
            
            # Tronquer les valeurs trop longues pour l'affichage
            session_uuid_display = (session_uuid[:15] + '...') if len(session_uuid) > 15 else session_uuid
            session_name_display = (session_name[:27] + '...') if len(session_name) > 30 else session_name
            
            print(f"{session_uuid_display:<40} | {session_name_display:<30} | {nb_draws:<15}")
        
        # Vérification des tirages pour la dernière session créée
        print("\nDétails des tirages pour la dernière session créée :")
        cur.execute("""
            SELECT session_uuid, name, total_draws, created_at 
            FROM unified_sessions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        last_session = cur.fetchone()
        if last_session:
            session_uuid = last_session[0]
            session_name = last_session[1]
            total_draws = last_session[2]
            created_at = last_session[3]
            
            print(f"\nDernière session créée :")
            print(f"- ID: {session_uuid}")
            print(f"- Nom: {session_name}")
            print(f"- Tirages totaux attendus: {total_draws}")
            print(f"- Créée le: {created_at}")
            
            # Vérifier les tirages pour cette session
            cur.execute("""
                SELECT 
                    draw_number, 
                    lottery_name,
                    draw_date,
                    winning_numbers
                FROM 
                    unified_draws 
                WHERE 
                    session_uuid = %s
                ORDER BY 
                    draw_number
                LIMIT 5
            """, (session_uuid,))
            
            draws = cur.fetchall()
            print(f"\n{len(draws)} premiers tirages trouvés :")
            for draw in draws:
                print(f"- Tirage {draw[0]}: {draw[1]} le {draw[2]} - Numéros: {draw[3]}")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la vérification des tirages: {e}")

if __name__ == "__main__":
    check_draws()
