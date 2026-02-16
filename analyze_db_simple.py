#!/usr/bin/env python3
import psycopg2

def analyze_database():
    configs = [
        {'name': 'katula_db', 'host': 'localhost', 'database': 'katula_db', 'user': 'postgres', 'password': 'admin123', 'port': 5432},
        {'name': 'katooling_main_system', 'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': 'Katula2024', 'port': 5432}
    ]
    
    session_keywords = ['session', 'work', 'projet', 'analysis']
    draw_keywords = ['draw', 'tirage', 'tirrage', 'resultat', 'loto', 'lottery', 'result', 'numero', 'number']
    
    for config in configs:
        print(f"\n{'='*50}")
        print(f"ANALYSE: {config['name']}")
        print(f"{'='*50}")
        
        try:
            conn = psycopg2.connect(
                host=config['host'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                port=config['port']
            )
            cursor = conn.cursor()
            print(f"Connexion reussie a {config['database']}")
            
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            all_tables = [t[0] for t in cursor.fetchall()]
            print(f"Total tables: {len(all_tables)}")
            
            session_tables = []
            draw_tables = []
            
            for table in all_tables:
                table_lower = table.lower()
                if any(keyword in table_lower for keyword in session_keywords):
                    session_tables.append(table)
                elif any(keyword in table_lower for keyword in draw_keywords):
                    draw_tables.append(table)
            
            if session_tables:
                print(f"\nTABLES DE SESSIONS ({len(session_tables)}):")
                for table in session_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"  {table}: {count} enregistrements")
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                            rows = cursor.fetchall()
                            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
                            columns = [col[0] for col in cursor.fetchall()]
                            
                            for i, row in enumerate(rows):
                                sample = dict(zip(columns[:3], row[:3]))
                                print(f"    Exemple {i+1}: {sample}")
                    except Exception as e:
                        print(f"    Erreur: {e}")
            
            if draw_tables:
                print(f"\nTABLES DE TIRAGES ({len(draw_tables)}):")
                for table in draw_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"  {table}: {count} enregistrements")
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                            rows = cursor.fetchall()
                            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
                            columns = [col[0] for col in cursor.fetchall()]
                            
                            for i, row in enumerate(rows):
                                sample = dict(zip(columns[:3], row[:3]))
                                print(f"    Exemple {i+1}: {sample}")
                    except Exception as e:
                        print(f"    Erreur: {e}")
            
            if not session_tables and not draw_tables:
                print("\nAucune table de session ou tirage trouvee")
                print("Tables disponibles:")
                for table in all_tables[:10]:
                    print(f"  - {table}")
                if len(all_tables) > 10:
                    print(f"  ... et {len(all_tables) - 10} autres")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Erreur connexion: {e}")

if __name__ == "__main__":
    analyze_database()