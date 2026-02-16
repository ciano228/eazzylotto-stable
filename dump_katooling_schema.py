
import psycopg2
import json

def dump_schema():
    conn = psycopg2.connect('dbname=katooling_main_system user=postgres password=Katulaa_33 host=localhost')
    cur = conn.cursor()
    
    # Get columns
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'combinations' ORDER BY ordinal_position")
    columns = cur.fetchall()
    
    # Get universe distinct values
    cur.execute("SELECT DISTINCT universe FROM combinations")
    universes = [row[0] for row in cur.fetchall()]
    
    # Get count
    cur.execute("SELECT count(*) FROM combinations")
    total_rows = cur.fetchone()[0]
    
    # Get sample row to see data
    cur.execute("SELECT * FROM combinations LIMIT 1")
    colnames = [desc[0] for desc in cur.description]
    sample_row = cur.fetchone()
    sample_data = dict(zip(colnames, sample_row)) if sample_row else {}

    result = {
        "columns": columns,
        "universes": universes,
        "total_rows": total_rows,
        "sample_data": sample_data
    }
    
    with open('katooling_schema_dump.json', 'w') as f:
        json.dump(result, f, indent=4)
    
    conn.close()
    print("Schema dumped successfully to katooling_schema_dump.json")

if __name__ == "__main__":
    dump_schema()
