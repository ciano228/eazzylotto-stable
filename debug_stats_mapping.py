
import psycopg2
import os
from dotenv import load_dotenv

# Load env vars same as server
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def debug_mapping():
    print("🔌 Connecting to DB with config:", DB_CONFIG)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Check if table exists
        cur.execute("SELECT to_regclass('public.combinations')")
        table_exists = cur.fetchone()[0]
        if not table_exists:
            print("❌ Table 'combinations' does NOT exist!")
            return

        print("✅ Table 'combinations' exists.")

        # 2. Count total rows
        cur.execute("SELECT COUNT(*) FROM combinations")
        total_rows = cur.fetchone()[0]
        print(f"📊 Total rows in 'combinations': {total_rows}")

        # 3. Check distinct universes
        cur.execute("SELECT DISTINCT univers FROM combinations")
        universes = cur.fetchall()
        print(f"🌍 Universes found: {[u[0] for u in universes]}")

        # 4. Filter by 'mundo'
        cur.execute("SELECT COUNT(*) FROM combinations WHERE LOWER(univers) = 'mundo'")
        mundo_count = cur.fetchone()[0]
        print(f"🔍 Rows for 'mundo' (case-insensitive): {mundo_count}")

        if mundo_count == 0:
             print("⚠️ No data for 'mundo'. This explains why stats are empty.")
        else:
             print("✅ Data found for 'mundo'. Stats engine 'load_universe_map' logic might be failing.")
             # Check distinct denominations
             cur.execute("SELECT COUNT(DISTINCT denomination) FROM combinations WHERE LOWER(univers) = 'mundo'")
             denom_count = cur.fetchone()[0]
             print(f"   Distinct denominations: {denom_count}")

    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    debug_mapping()
