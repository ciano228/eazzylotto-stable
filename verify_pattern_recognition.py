import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.pattern_recognition_service import PatternRecognitionService

def verify_pattern_recognition():
    print("🚀 Verifying Pattern Recognition Service...")
    
    # Setup DB
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # SQLAlchemy setup
    DATABASE_URL = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        service = PatternRecognitionService(db_config)
        
        # Test Case 1: Generate Signature
        target = [70, 89, 54, 25, 34]
        universe = "mundo"
        print(f"\n🧪 Generating signature for {target} in {universe}...")
        
        signature = service.generate_draw_signature(target, universe)
        if signature:
            print(f"✅ Signature Generated! ({len(signature)} pairs)")
            print(f"Sample Pair 1 Attributes: {json.dumps(signature[0], indent=2)}")
        else:
            print("❌ Failed to generate signature.")
            return

        # Test Case 2: Find Similar Draws
        print("\n🔍 Finding similar draws (Threshold 50%)...")
        results = service.find_similar_draws(db, target, universe, min_match_percent=50)
        
        print(f"Found {results['total_matches']} matches.")
        
        if results['matches']:
            top_match = results['matches'][0]
            print(f"🏆 Top Match: {top_match['draw_numbers']} (Score: {top_match['match_score']}%) on {top_match['draw_date']}")
        else:
            print("⚠️ No matches found (this might be normal if DB is small/empty or numbers are unique).")
            
        # Test Case 3: Consequences
        print("\n🔮 Analyzing Consequences...")
        consequences = results.get('consequences', {})
        if 'most_frequent_numbers' in consequences:
            print("Top predicted numbers following this pattern:")
            for item in consequences['most_frequent_numbers'][:5]:
                print(f"  # {item['number']} (Freq: {item['frequency']}%)")
                
        if 'most_frequent_pairs' in consequences:
            print("\nTop predicted PAIRS following this pattern:")
            for item in consequences['most_frequent_pairs'][:5]:
                print(f"  # {item['pair']} (Freq: {item['frequency']}%)")
                
        if 'most_frequent_attributes' in consequences:
            print("\nTop predicted ATTRIBUTES following this pattern:")
            for attr_type, stats in consequences['most_frequent_attributes'].items():
                if stats:
                    top = stats[0]
                    print(f"  # {attr_type}: {top['value']} (Freq: {top['frequency']}%)")
        else:
            print("No consequences analyzed.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_pattern_recognition()
