
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def inspect_structure():
    print("🕵️‍♂️ Inspecting 'mundo' combinations structure...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get sample rows
        cur.execute("""
            SELECT chip, denomination, num1, num2, combination, forme, tome 
            FROM combinations 
            WHERE univers='mundo' 
            LIMIT 20
        """)
        rows = cur.fetchall()
        
        print(f"{'CHIP':<10} {'DENOM':<10} {'NUM1':<6} {'NUM2':<6} {'COMBINATION':<15} {'FORME':<10}")
        print("-" * 70)
        for r in rows:
            print(f"{str(r[0]):<10} {str(r[1]):<10} {str(r[2]):<6} {str(r[3]):<6} {str(r[4]):<15} {str(r[5]):<10}")

        # Check if 49 or 87 exists in num1/num2
        print("\n🔍 Checking for 49 or 87 in num1/num2/combination...")
        cur.execute("""
            SELECT chip, combination, num1, num2 
            FROM combinations 
            WHERE univers='mundo' 
            AND (num1 IN ('49', '87') OR num2 IN ('49', '87') OR combination LIKE '%49%' OR combination LIKE '%87%')
        """)
        matches = cur.fetchall()
        if matches:
            for m in matches:
                print(f"   MATCH: {m}")
        else:
            print("   ❌ Number 49 or 87 NOT FOUND in num1/num2 columns for 'mundo'.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    inspect_structure()
