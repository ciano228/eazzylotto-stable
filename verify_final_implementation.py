
import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup environment
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.session_statistics_engine import SessionStatisticsEngine
except ImportError as e:
    print(f"CRITICAL: Could not import SessionStatisticsEngine. {e}")
    sys.exit(1)

def verify_full_implementation():
    print("STARTING FINAL VERIFICATION: Session 2 + Pair Logic + Full Attributes")
    
    # 1. Setup DB Connection
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
        
        # 2. Get Real Draw Data for Session 2
        print("Fetching draws for Session 2...")
        cur.execute("SELECT draw_number, winning_numbers, draw_date, lottery_name FROM session_draws WHERE session_id = 2 ORDER BY draw_number")
        draws = cur.fetchall()
        
        if not draws:
            print("No draws found for Session 2!")
            return
            
        print(f"Loaded {len(draws)} draws.")
        
        # 3. Run the Engine
        print("Running SessionStatisticsEngine.calculate_stats()...")
        engine = SessionStatisticsEngine(db_config)
        
        # We need to adapt the raw rows to what the engine expects if needed,
        # but the engine expects a list of dicts with 'winning_numbers' which we have.
        # Ensure winning_numbers is a list of ints
        processed_draws = []
        for d in draws:
            d_obj = dict(d)
            # winning_numbers usually comes as list from PG array, but let's ensure
            processed_draws.append(d_obj)
            
        stats = engine.calculate_stats(processed_draws, 'mundo')
        
        # 4. Analyze Results
        if not stats:
            print("RESULT: Engine returned Empty Stats!")
            return
            
        print("\nVERIFICATION REPORT")
        print("-------------------------------")
        
        # Check all required keys
        required_keys = [
            'forme', 'tome', 'granque', 'petique', 
            'engine', 'beastie', 'alpha_ranking', 'chip', 'denomination',
            'ligne', 'colonne',
            'parite', 'region', 'gentile', 'quartier', 'base_name'
        ]
        
        all_present = True
        for key in required_keys:
            if key in stats:
                count = len(stats[key])
                print(f"Attribute '{key}': FOUND ({count} unique values)")
                
                # Print top 3 for manual sanity check
                # Convert to list and sort purely for display
                # items is already a list of dicts
                items = list(stats[key])
                items.sort(key=lambda x: x['count'], reverse=True)
                
                for item in items[:3]:
                    val = item.get('value', '???')
                    cnt = item.get('count', 0)
                    try:
                         # Safe print for unicode
                        safe_val = str(val).encode('ascii', 'ignore').decode('ascii')
                        print(f"   - {safe_val}: {cnt}")
                    except:
                        print(f"   - (Encoding Error): {cnt}")
            else:
                print(f"Attribute '{key}': MISSING")
                all_present = False

        print("-------------------------------")
        if all_present:
            print("SUCCESS: All requested attributes are being tracked on real data.")
        else:
            print("WARNING: Some attributes are missing.")
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    verify_full_implementation()
