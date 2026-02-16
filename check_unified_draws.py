import psycopg2

def check_unified_draws():
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
        print("=== Structure de la table unified_draws ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'unified_draws'
            ORDER BY ordinal_position
        """)
        
        print("\nColonnes de la table unified_draws :")
        print("-" * 80)
        print(f"{'Nom':<25} | {'Type':<20} | Nullable | Valeur par défaut")
        print("-" * 80)
        
        for col in cur.fetchall():
            print(f"{col[0]:<25} | {col[1]:<20} | {col[2]:<8} | {col[3]}")
        
        # Vérification du nombre de tirages pour session_test_001
        cur.execute("""
            SELECT COUNT(*) 
            FROM unified_draws d
            JOIN unified_sessions s ON d.session_uuid = s.session_uuid
            WHERE s.name = 'session_test_001'
        """)
        
        count = cur.fetchone()[0]
        print(f"\n\nNombre de tirages pour session_test_001: {count}")
        
        # Vérification des premiers tirages
        if count > 0:
            print("\nDétails des 5 premiers tirages :")
            print("-" * 100)
            
            cur.execute("""
                SELECT d.* 
                FROM unified_draws d
                JOIN unified_sessions s ON d.session_uuid = s.session_uuid
                WHERE s.name = 'session_test_001'
                ORDER BY d.draw_number
                LIMIT 5
            """)
            
            draws = cur.fetchall()
            for i, draw in enumerate(draws, 1):
                print(f"\nTirage {i}:")
                for j, value in enumerate(draw):
                    col_name = cur.description[j].name if cur.description else f"Colonne {j+1}"
                    print(f"- {col_name}: {value}")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la vérification de la table unified_draws: {e}")

if __name__ == "__main__":
    check_unified_draws()
