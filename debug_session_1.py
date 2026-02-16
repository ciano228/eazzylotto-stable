
import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def analyze_session_1():
    print("🕵️‍♂️ Analyzing Session 1 Data Source Truth...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Get Draws
        cur.execute("SELECT draw_number, winning_numbers FROM session_draws WHERE session_id = 1 ORDER BY draw_number")
        draws = cur.fetchall()
        
        if not draws:
             print("❌ No draws found for Session 1")
             return

        print(f"📄 Found {len(draws)} draws.")
        
        # 2. Build Cache of Mapping for drawn numbers only
        # We need to know what the DB says for these specific numbers.
        all_numbers = set()
        for _, nums in draws:
            for n in nums:
                all_numbers.add(str(n))
        
        print(f"🔢 Unique numbers drawn: {len(all_numbers)}")
        
        # Query mapping
        placeholders = ','.join(['%s'] * len(all_numbers))
        
        # Check carefully: Does the user expect 'univers' to be something specific?
        # We'll check 'mundo' first as it seems default.
        query = f"""
            SELECT chip, denomination, forme, tome 
            FROM combinations 
            WHERE univers = 'mundo' 
            AND (chip IN ({placeholders}) OR denomination IN ({placeholders}))
        """
        # We pass the list twice to match placeholders
        params = list(all_numbers) + list(all_numbers)
        # Actually simplest is to fetch ALL for mundo and filter in python to handle complex matching logic
        cur.execute("SELECT chip, denomination, forme, tome FROM combinations WHERE univers = 'mundo'")
        mapping_rows = cur.fetchall()
        
        # Build lookup: Number -> Attributes
        # Using the same logic as the Engine (Chip match first, then Denom)
        lookup = {}
        
        # Helper to normalize key
        def add_to_lookup(k, attrs):
            k_str = str(k)
            # clean chip
            if k_str.lower().startswith('chip'):
                 k_str = k_str.lower().replace('chip', '')
            # clean int
            if k_str.isdigit():
                 lookup[str(int(k_str))] = attrs
            else:
                 lookup[k_str] = attrs

        for row in mapping_rows:
            chip, denom, forme, tome = row
            attrs = {'forme': forme, 'tome': tome}
            
            if chip: add_to_lookup(chip, attrs)
            if denom: add_to_lookup(denom, attrs)
            
        
        # 3. Re-calculate Manual Count
        stats = defaultdict(int)
        
        print("\n📝 Detail per Draw:")
        for i, (d_num, nums) in enumerate(draws):
            print(f"  Draw {d_num}: {nums}")
            for n in nums:
                n_str = str(n)
                if n_str in lookup:
                    attrs = lookup[n_str]
                    print(f"    - {n}: Forme={attrs['forme']}, Tome={attrs['tome']}")
                    stats[f"Forme: {attrs['forme']}"] += 1
                    stats[f"Tome: {attrs['tome']}"] += 1
                else:
                    print(f"    - {n}: ⚠️ NO MAPPING FOUND (Unknown)")
        
        print("\n📊 CALCULATED TOTALS (DB Truth):")
        for k, v in sorted(stats.items()):
            print(f"  {k}: {v}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    analyze_session_1()
