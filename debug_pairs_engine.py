
import os
import sys
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.session_statistics_engine import SessionStatisticsEngine
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_engine_pairs():
    print("Starting Engine Pair Logic Debug...")
    
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    engine = SessionStatisticsEngine(db_config)
    
    dummy_draws = [
        {
            'draw_number': 2,
            'draw_date': '2024-01-01',
            'winning_numbers': [52, 12, 17, 24, 82],
            'lottery_name': 'Debug Draw'
        }
    ]
    
    print(f"Testing with universe='mundo' and Draw 2: {dummy_draws[0]['winning_numbers']}")
    
    stats = engine.calculate_stats(dummy_draws, 'mundo')
    
    print(f"\nStats Result:")
    if not stats:
        print("Stats object is EMPTY.")
    else:
        check_cats = [
            'engine', 'beastie', 'chip', 'denomination', 'alpha_ranking', 
            'forme', 'tome', 'base_name', 'parite', 'region', 'gentile', 'quartier'
        ]
        print(f"Checking Categories: {check_cats}")
        for k in check_cats:
            if k in stats:
                print(f"   Category '{k}': {len(stats[k])} items found.")
                for item in stats[k][:3]:
                    val_str = str(item['value']).encode('ascii', 'ignore').decode('ascii')
                    print(f"     - {val_str}: Count={item['count']}")
            else:
                print(f"   WARNING: Category '{k}' NOT FOUND in stats.")

if __name__ == "__main__":
    test_engine_pairs()
