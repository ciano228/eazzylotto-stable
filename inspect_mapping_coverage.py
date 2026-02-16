
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

def check_coverage():
    print("🕵️‍♂️ Checking Mapping Coverage for 'mundo'...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check Total distinct chips
        cur.execute("SELECT COUNT(DISTINCT chip) FROM combinations WHERE univers='mundo'")
        total = cur.fetchone()[0]
        print(f"📄 Total Mapped Chips: {total}")
        
        # Check Range
        cur.execute("""
            SELECT MIN(NULLIF(regexp_replace(chip, '[^0-9]', '', 'g'), '')::int), 
                   MAX(NULLIF(regexp_replace(chip, '[^0-9]', '', 'g'), '')::int)
            FROM combinations 
            WHERE univers='mundo'
        """)
        min_val, max_val = cur.fetchone()
        print(f"🔢 ID Range: {min_val} - {max_val}")
        
        # Check specific missing numbers from Session 1 (49, 87, 52, 65, 82)
        missing_suspects = ['chip49', 'chip87', 'chip52', 'chip65', 'chip82']
        placeholders = ','.join(['%s'] * len(missing_suspects))
        cur.execute(f"SELECT chip FROM combinations WHERE univers='mundo' AND chip IN ({placeholders})", missing_suspects)
        found = [r[0] for r in cur.fetchall()]
        
        print("\n🔍 Investigating Specific Suspects:")
        for m in missing_suspects:
            status = "✅ Found" if m in found else "❌ MISSING"
            print(f"   - {m}: {status}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_coverage()
