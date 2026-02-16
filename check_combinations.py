import psycopg2
from psycopg2.extras import RealDictCursor
import json

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def check_combinations():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("--- Testing specific pair 65-76 ---")
        cursor.execute("SELECT num1, num2, univers, combination, forme FROM combinations WHERE (num1 = 65 AND num2 = 76) OR (num1 = 76 AND num2 = 65)")
        rows = cursor.fetchall()
        print(json.dumps(rows, indent=2))
        
        print("\n--- Testing numbers individually ---")
        cursor.execute("SELECT num1, num2, univers FROM combinations WHERE num1 = 65 LIMIT 5")
        rows = cursor.fetchall()
        print(f"Num1=65 matches: {len(rows)}")
        print(json.dumps(rows, indent=2))
        
        cursor.execute("SELECT num1, num2, univers FROM combinations WHERE num1 = 76 LIMIT 5")
        rows = cursor.fetchall()
        print(f"Num1=76 matches: {len(rows)}")
        print(json.dumps(rows, indent=2))
        
        print("\n--- Checking database universes ---")
        cursor.execute("SELECT DISTINCT univers FROM combinations")
        rows = cursor.fetchall()
        print(json.dumps(rows, indent=2))
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_combinations()
