#!/usr/bin/env python3
"""
Analyser la vraie structure de la table Katula
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def analyze_katula_structure():
    """Analyser en détail la structure de table_de_katula"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        
        cursor = conn.cursor()
        
        print("=== STRUCTURE COMPLETE TABLE_DE_KATULA ===")
        
        # Structure des colonnes
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nColonnes:")
        for col in columns:
            print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        # Analyser les données par univers
        cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
        universes = cursor.fetchall()
        print(f"\nUniviers disponibles: {[u[0] for u in universes]}")
        
        for universe in universes:
            universe_name = universe[0]
            print(f"\n=== UNIVERS: {universe_name.upper()} ===")
            
            # Compter les entrées
            cursor.execute("SELECT COUNT(*) FROM table_de_katula WHERE univers = %s", (universe_name,))
            count = cursor.fetchone()[0]
            print(f"Total entrées: {count}")
            
            # Analyser les positions uniques
            cursor.execute("""
                SELECT DISTINCT ligne, colonne 
                FROM table_de_katula 
                WHERE univers = %s 
                ORDER BY ligne, colonne
            """, (universe_name,))
            positions = cursor.fetchall()
            print(f"Positions uniques: {len(positions)}")
            
            # Analyser les formes
            cursor.execute("""
                SELECT forme, COUNT(*) 
                FROM table_de_katula 
                WHERE univers = %s 
                GROUP BY forme 
                ORDER BY COUNT(*) DESC
            """, (universe_name,))
            formes = cursor.fetchall()
            print(f"Formes: {dict(formes)}")
            
            # Analyser les dénominations
            cursor.execute("""
                SELECT denomination, COUNT(*) 
                FROM table_de_katula 
                WHERE univers = %s 
                GROUP BY denomination 
                ORDER BY COUNT(*) DESC
            """, (universe_name,))
            denominations = cursor.fetchall()
            print(f"Dénominations: {dict(list(denominations)[:5])}...")
            
            # Analyser les pétiques (zones géométriques)
            cursor.execute("""
                SELECT petique, COUNT(*) 
                FROM table_de_katula 
                WHERE univers = %s 
                GROUP BY petique 
                ORDER BY COUNT(*) DESC
            """, (universe_name,))
            petiques = cursor.fetchall()
            print(f"Pétiques: {dict(petiques)}")
            
            # Voir quelques exemples complets
            cursor.execute("""
                SELECT chip_id, ligne, colonne, chip, forme, denomination, petique
                FROM table_de_katula 
                WHERE univers = %s 
                ORDER BY ligne, colonne
                LIMIT 5
            """, (universe_name,))
            examples = cursor.fetchall()
            print("Exemples:")
            for ex in examples:
                print(f"  {ex[1]}-{ex[2]}: {ex[3]} | {ex[4]} | {ex[5]} | Zone:{ex[6]}")
        
        # Analyser les tables spécialisées par univers et forme
        print("\n=== TABLES SPECIALISEES ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'table_de_katula_%'
            ORDER BY table_name
        """)
        specialized_tables = cursor.fetchall()
        
        for table in specialized_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} entrées")
            
            if count > 0:
                # Voir la structure
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    ORDER BY ordinal_position
                """)
                cols = [c[0] for c in cursor.fetchall()]
                print(f"  Colonnes: {', '.join(cols)}")
                
                # Voir un exemple
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                example = cursor.fetchone()
                if example:
                    print(f"  Exemple: {str(example)[:100]}...")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    analyze_katula_structure()