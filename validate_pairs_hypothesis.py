
import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict
import itertools

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def validate_pairs():
    print("Validating Pair-Based Hypothesis for Session 2...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Load Draws
        cur.execute("SELECT draw_number, winning_numbers FROM session_draws WHERE session_id = 2 ORDER BY draw_number")
        draws = cur.fetchall()
        print(f"Loaded {len(draws)} draws for Session 2.")
        
        # 2. Load Mapping (Pair -> Attributes)
        # We assume the DB has columns num1, num2.
        print("Loading Pair Map from DB...")
        cur.execute("""
            SELECT num1, num2, forme, tome 
            FROM combinations 
            WHERE univers='mundo' 
        """)
        # Dictionary key: tuple (min(n1,n2), max(n1,n2)) -> attrs
        pair_map = {}
        for row in cur.fetchall():
            n1, n2, forme, tome = row
            if n1 and n2:
                # Store normalized pair
                pair_key = tuple(sorted([int(n1), int(n2)]))
                pair_map[pair_key] = {'forme': forme, 'tome': tome}
        
        print(f"Map Loaded: {len(pair_map)} unique pairs.")
        
        # 3. Process Draws
        stats = defaultdict(int)
        
        print("\nProcessing Draws (Pairwise):")
        for d_num, nums in draws:
            if not nums or len(nums) < 2: 
                continue
                
            # Generate all pairs
            pairs = list(itertools.combinations(nums, 2))
            
            # Print valid pairs found
            found_pairs = []
            for p in pairs:
                p_key = tuple(sorted([int(p[0]), int(p[1])]))
                if p_key in pair_map:
                    attrs = pair_map[p_key]
                    stats[f"Forme: {attrs['forme']}"] += 1
                    stats[f"Tome: {attrs['tome']}"] += 1
                    found_pairs.append(f"{p_key}:{attrs['forme']}")
            
            print(f"  Draw {d_num} {nums} -> Found {len(found_pairs)} valid pairs: {found_pairs}")

        print("\nHYPOTHESIS RESULTS (Should match User Manual Count):")
        print("Expected: Carre=4 ? Cercle=6 ? Triangle=2 ? Rectangle=2 ?")
        for k, v in sorted(stats.items()):
            print(f"  {k}: {v}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    validate_pairs()
