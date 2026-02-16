
import psycopg2
import json

def get_columns_raw():
    try:
        conn = psycopg2.connect('dbname=katooling_main_system user=postgres password=Katulaa_33 host=localhost')
        cur = conn.cursor()
        
        # 1. Get Column Names
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations' ORDER BY ordinal_position")
        columns = [row[0] for row in cur.fetchall()]
        
        # 2. Get Sample Data (Mundo)
        # Check if column is 'univers' or 'universe'
        univers_col = "univers" if "univers" in columns else "universe"
        
        cur.execute(f"SELECT * FROM combinations WHERE {univers_col} = 'mundo' LIMIT 1")
        sample = cur.fetchone()
        sample_data = dict(zip(columns, sample)) if sample else {}
        
        # 3. Save to fixed path
        output_file = r'C:\Users\User\eazzycalculator\combinations_final_schema.json'
        with open(output_file, 'w') as f:
            json.dump({"columns": columns, "sample": sample_data}, f, indent=4)
        print(f"DONE: {len(columns)} columns saved to {output_file}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    get_columns_raw()
