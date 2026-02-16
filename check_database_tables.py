import psycopg2
from psycopg2 import sql
from tabulate import tabulate

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname="katooling_main_system",
            user="postgres",
            password="Katulaa_33",
            host="localhost",
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def list_all_tables(conn):
    """Liste toutes les tables de la base de données."""
    try:
        with conn.cursor() as cur:
            # Requête pour lister toutes les tables dans le schéma public
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]
            return tables
    except Exception as e:
        print(f"Erreur lors de la récupération des tables: {e}")
        return []

def check_table_columns(conn, table_name):
    """Vérifie les colonnes d'une table spécifique."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur lors de la vérification des colonnes de {table_name}: {e}")
        return []

def check_table_row_count(conn, table_name):
    """Compte le nombre de lignes dans une table spécifique."""
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
            return cur.fetchone()[0]
    except Exception as e:
        print(f"Erreur lors du comptage des lignes de {table_name}: {e}")
        return 0

def main():
    conn = get_db_connection()
    if not conn:
        return

    try:
        # Lister toutes les tables
        print("\n=== Liste des tables dans la base de données ===")
        tables = list_all_tables(conn)
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        # Filtrer les tables liées aux sessions et aux tirages
        session_tables = [t for t in tables if 'session' in t.lower() or 'draw' in t.lower() or 'tirage' in t.lower()]
        
        print("\n=== Tables liées aux sessions et tirages ===")
        if not session_tables:
            print("Aucune table liée aux sessions ou aux tirages trouvée.")
            return

        # Afficher les informations sur les tables de sessions/tirages
        table_data = []
        for table in session_tables:
            row_count = check_table_row_count(conn, table)
            columns = check_table_columns(conn, table)
            table_data.append({
                'Table': table,
                'Lignes': row_count,
                'Colonnes': ", ".join([f"{col[0]} ({col[1]})" for col in columns[:3]])
            })
            
            # Afficher plus de détails pour les tables avec des données
            if row_count > 0:
                print(f"\n=== Contenu de la table {table} (premières 5 lignes) ===")
                try:
                    with conn.cursor() as cur:
                        cur.execute(sql.SQL("SELECT * FROM {} LIMIT 5").format(sql.Identifier(table)))
                        colnames = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        print(tabulate(rows, headers=colnames, tablefmt='grid'))
                except Exception as e:
                    print(f"Impossible d'afficher le contenu de {table}: {e}")

        # Afficher le résumé des tables
        print("\n=== Résumé des tables de sessions/tirages ===")
        print(tabulate(table_data, headers='keys', tablefmt='grid'))

    except Exception as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
