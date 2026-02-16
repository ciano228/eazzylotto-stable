"""
Script pour créer une session de test dans la base de données
"""

def create_test_session():
    try:
        import psycopg2
        import json
        from datetime import datetime, timedelta
        import random
        
        # Configuration de la base de données
        db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
        
        print("Connexion à la base de données...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Créer une nouvelle session
        import uuid
        session_uuid = str(uuid.uuid4())
        session_name = "Test_Session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        total_draws = 7  # Une semaine de tirages
        numbers_per_draw = 5
        number_range_min = 1
        number_range_max = 90
        
        # Insérer la session
        cursor.execute("""
            INSERT INTO unified_sessions 
            (session_uuid, name, description, total_draws, numbers_per_draw, 
             number_range_min, number_range_max, created_at, is_active, source_table)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING session_uuid
        """, (
            session_uuid,
            session_name,
            "Session de test créée automatiquement",
            total_draws,
            numbers_per_draw,
            number_range_min,
            number_range_max,
            datetime.now(),
            True,
            'unified_sessions'
        ))
        
        session_uuid = cursor.fetchone()[0]
        print(f"Session créée avec l'ID: {session_uuid}")
        
        # Ajouter des tirages de test
        loto_days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        
        for i in range(total_draws):
            draw_date = datetime.now() - timedelta(days=total_draws - i - 1)
            draw_number = i + 1
            lottery_name = f"loto_{loto_days[i]}"
            
            # Générer des numéros aléatoires
            numbers = sorted(random.sample(range(number_range_min, number_range_max + 1), numbers_per_draw))
            
            cursor.execute("""
                INSERT INTO unified_draws 
                (session_uuid, draw_number, lottery_name, draw_date, 
                 winning_numbers, is_completed, cycle_position)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_uuid,
                draw_number,
                lottery_name,
                draw_date,
                numbers,
                True,  # is_completed
                i % 7  # cycle_position (0-6 pour les 7 jours)
            ))
        
        conn.commit()
        print(f"{total_draws} tirages ajoutés à la session")
        
        # Vérifier que la session est bien enregistrée
        cursor.execute("""
            SELECT s.name, s.total_draws, COUNT(d.draw_number) as draws_count
            FROM unified_sessions s
            LEFT JOIN unified_draws d ON s.session_uuid = d.session_uuid
            WHERE s.session_uuid = %s
            GROUP BY s.name, s.total_draws
        """, (session_uuid,))
        
        session_info = cursor.fetchone()
        print(f"\nVérification de la session:")
        print(f"- Nom: {session_info[0]}")
        print(f"- Tirages prévus: {session_info[1]}")
        print(f"- Tirages enregistrés: {session_info[2]}")
        
        cursor.close()
        conn.close()
        
        print("\nTest réussi! La session de test a été créée avec succès.")
        print(f"\nVous pouvez maintenant vérifier la session dans l'application:")
        print(f"1. Allez sur http://localhost:8881/frontend/katula-temporal-analysis.html")
        print(f"2. Sélectionnez la session '{session_name}' dans la liste déroulante")
        
        return True
        
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    import sys
    
    print("=== CRÉATION D'UNE SESSION DE TEST ===\n")
    
    try:
        success = create_test_session()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERREUR CRITIQUE: {str(e)}")
        sys.exit(1)
