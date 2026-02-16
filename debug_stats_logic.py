
import os
import sys
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load env vars
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.session_statistics_engine import SessionStatisticsEngine
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def test_engine():
    print("🚀 Starting Logic Debug...")
    
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    engine = SessionStatisticsEngine(db_config)
    
    # Test specific numbers that we know should exist in 'mundo' (e.g. 1 to 5)
    test_numbers = [1, 2, 3, 4, 5, 10, 20] 
    
    dummy_draws = [
        {
            'draw_number': 1,
            'draw_date': '2024-01-01',
            'winning_numbers': test_numbers,
            'lottery_name': 'Debug Draw'
        }
    ]
    
    print(f"🧪 Testing with universe='mundo' and numbers: {test_numbers}")
    
    # 1. Test loading map manually
    mapping = engine._load_universe_map('mundo')
    print(f"🗺️ Map loaded: {len(mapping)} keys.")
    print(f"🔑 Sample keys: {list(mapping.keys())[:20]}")
    
    # Check if our test numbers are in the map
    for n in test_numbers:
        s = str(n)
        if s in mapping:
            print(f"   ✅ Number '{s}' found in map. Attributes: {mapping[s][0]}")
        else:
            print(f"   ❌ Number '{s}' NOT found in map.")
            
    # 2. Test calculate_stats
    stats = engine.calculate_stats(dummy_draws, 'mundo')
    
    print(f"\n📊 Stats Result Keys: {list(stats.keys())}")
    if not stats:
        print("❌ Stats object is EMPTY.")
    else:
        for k, v in stats.items():
            print(f"   category '{k}': {len(v)} items")
            if v:
                print(f"     sample: {v[0]}")

if __name__ == "__main__":
    test_engine()
