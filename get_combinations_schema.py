
import psycopg2
import json

def get_columns():
    try:
        conn = psycopg2.connect('dbname=katooling_main_system user=postgres password=Katulaa_33 host=localhost')
        cur = conn.cursor()
        
        # Get all columns
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations' ORDER BY ordinal_position")
        columns = [row[0] for row in cur.fetchall()]
        
        # Get sample row
        cur.execute("SELECT * FROM combinations LIMIT 1")
        sample = cur.fetchone()
        sample_dict = dict(zip(columns, sample)) if sample else {}
        
        # Check universe column name
        univers_col = "univers" if "univers" in columns else "universe"
        
        cur.execute(f"SELECT DISTINCT {univers_col} FROM combinations")
        universes = [row[0] for row in cur.fetchall()]
        
        result = {
            "columns": columns,
            "universes": universes,
            "sample": sample_dict
        }
        
        with open('combinations_schema.json', 'w') as f:
            json.dump(result, f, indent=4)
        
        print(f"Success: {len(columns)} columns found.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_columns()
