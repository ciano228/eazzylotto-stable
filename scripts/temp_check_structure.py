import psycopg2
import psycopg2.extras

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def check_table_structure():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        
        # Vérifier la structure de la table
        print("\n=== Structure de table_de_katula ===")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' 
            ORDER BY ordinal_position;
        """)
        for col in cur.fetchall():
            print(f"{col[0]}: {col[1]}{f'({col[2]})' if col[2] else ''}")
            
        # Vérifier les premières lignes de données
        print("\n=== Exemple de données ===")
        cur.execute("SELECT * FROM table_de_katula LIMIT 3")
        rows = cur.fetchall()
        if rows:
            print(f"Nombre de colonnes: {len(rows[0])}")
            print("Premières lignes:")
            for row in rows:
                print(row)
        else:
            print("Aucune donnée trouvée")
            
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure()