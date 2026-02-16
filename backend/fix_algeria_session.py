#!/usr/bin/env python3
import psycopg2
import json

def fix_algeria_session():
    """Corrige l'accès à la session algeria"""
    
    # Essayer les deux mots de passe
    passwords = ['Katula2024', 'Katulaa_33']
    conn = None
    
    for password in passwords:
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='katula_db',
                user='postgres',
                password=password
            )
            print(f"Connexion réussie avec {password}")
            break
        except Exception as e:
            print(f"Échec connexion avec {password}: {e}")
            continue
    
    if not conn:
        print("Impossible de se connecter à la base de données")
        return
    
    cursor = conn.cursor()
    
    try:
        # Vérifier les sessions disponibles
        cursor.execute("SELECT id, name FROM work_sessions ORDER BY id")
        sessions = cursor.fetchall()
        print("\nSessions disponibles:")
        for session_id, name in sessions:
            print(f"  {session_id}: {name}")
        
        # Chercher la session algeria
        cursor.execute("SELECT id, name FROM work_sessions WHERE name ILIKE '%algeria%'")
        algeria_sessions = cursor.fetchall()
        
        if algeria_sessions:
            print(f"\nSessions Algeria trouvées:")
            for session_id, name in algeria_sessions:
                print(f"  ID: {session_id}, Nom: {name}")
                
                # Vérifier les tirages pour cette session
                cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
                draw_count = cursor.fetchone()[0]
                print(f"    Nombre de tirages: {draw_count}")
        else:
            print("\nAucune session Algeria trouvée")
            
        # Vérifier si unified_sessions existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'unified_sessions'
            )
        """)
        unified_exists = cursor.fetchone()[0]
        
        if unified_exists:
            cursor.execute("SELECT session_id, session_name FROM unified_sessions WHERE session_name ILIKE '%algeria%'")
            unified_algeria = cursor.fetchall()
            print(f"\nSessions Algeria dans unified_sessions:")
            for session_id, name in unified_algeria:
                print(f"  ID: {session_id}, Nom: {name}")
        else:
            print("\nTable unified_sessions n'existe pas")
            
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_algeria_session()