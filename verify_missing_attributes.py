
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def check_data_sparsity():
    print("Checking Data Sparsity for Missing Attributes...")
    
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check specifically for chip8 and chip10
        print("\nInspecting Chip 8 and 10:")
        cur.execute("SELECT chip, num1, num2, base_name FROM combinations WHERE univers='mundo' AND chip IN ('chip8', 'chip10')")
        rows = cur.fetchall()
        for r in rows:
            print(f"  {r['chip']} ({r['num1']}-{r['num2']}): '{r['base_name']}' type={type(r['base_name'])}")
        
        # Check if any OTHER attributes are sparse?
        attrs = ['region', 'quartier', 'gentile', 'parite_id']
        for attr in attrs:
            cur.execute(f"SELECT COUNT(*) as count FROM combinations WHERE univers='mundo' AND {attr} IS NOT NULL")
            c = cur.fetchone()['count']
            print(f"Total Combinations with '{attr}': {c}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_data_sparsity()
