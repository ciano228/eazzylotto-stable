
import psycopg2

db_config = {
    'dbname': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'host': 'localhost',
    'port': '5432'
}

def analyze_pattern():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    queries = {
        "Total Combinations (Mundo)": "SELECT count(*) FROM combinations WHERE univers = 'mundo'",
        "Rectangle Only": "SELECT count(*) FROM combinations WHERE univers = 'mundo' AND forme = 'rectangle'",
        "Tome1 Only": "SELECT count(*) FROM combinations WHERE univers = 'mundo' AND tome = 'tome1'",
        "Rectangle + Tome1 (Composite)": "SELECT count(*) FROM combinations WHERE univers = 'mundo' AND forme = 'rectangle' AND tome = 'tome1'",
        "Rectangle + Tome2": "SELECT count(*) FROM combinations WHERE univers = 'mundo' AND forme = 'rectangle' AND tome = 'tome2'",
        "Cercle + Tome1": "SELECT count(*) FROM combinations WHERE univers = 'mundo' AND forme = 'cercle' AND tome = 'tome1'"
    }
    
    print(f"\n{'='*50}")
    print(f"PATTERN COMBINATION ANALYSIS (DATABASE)")
    print(f"{'='*50}")
    
    for label, sql in queries.items():
        cur.execute(sql)
        count = cur.fetchone()[0]
        print(f"{label:30}: {count} combos")
        
    conn.close()

if __name__ == "__main__":
    analyze_pattern()
