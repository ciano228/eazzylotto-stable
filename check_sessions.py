import psycopg2
from datetime import datetime

def check_unified_sessions():
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
        
        # Vérification de la table unified_sessions
        print("Vérification de la table 'unified_sessions'...")
        
        # Récupération de toutes les colonnes de la table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'unified_sessions'
        """)
        columns = cur.fetchall()
        print("\nStructure de la table 'unified_sessions':")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
        # Comptage des enregistrements
        cur.execute("SELECT COUNT(*) FROM unified_sessions")
        count = cur.fetchone()[0]
        print(f"\nNombre total de sessions: {count}")
        
        # Récupération des 10 premières sessions
        if count > 0:
            print("\nDétails des sessions (10 premières) :")
            cur.execute("""
                SELECT session_uuid, name, description, total_draws, 
                       created_at, is_active, source_table
                FROM unified_sessions 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            sessions = cur.fetchall()
            for i, session in enumerate(sessions, 1):
                print(f"\n--- Session {i} ---")
                print(f"ID: {session[0]}")
                print(f"Nom: {session[1]}")
                print(f"Description: {session[2]}")
                print(f"Tirages totaux: {session[3]}")
                print(f"Créée le: {session[4]}")
                print(f"Active: {session[5]}")
                print(f"Source: {session[6]}")
        
        # Vérification de la table unified_draws
        print("\n\nVérification de la table 'unified_draws'...")
        cur.execute("SELECT COUNT(*) FROM unified_draws")
        draws_count = cur.fetchone()[0]
        print(f"Nombre total de tirages enregistrés: {draws_count}")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la vérification des sessions: {e}")

if __name__ == "__main__":
    check_unified_sessions()
