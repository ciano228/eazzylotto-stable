
import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup environment
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend')) # Path fix
sys.path.append(os.path.dirname(__file__))

try:
    from backend.app.services.correlation_service import CorrelationService
except ImportError as e:
    print(f"Import Error: {e}")
    # Try alternate path if backend is root
    sys.path.append("c:\\Users\\User\\eazzycalculator")
    from backend.app.services.correlation_service import CorrelationService

def verify_correlations():
    print("STARTING CORRELATION SERVICE VERIFICATION...")
    
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Get Session 2 Data
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print("Fetching draws for Session 2...")
        cur.execute("SELECT draw_number, winning_numbers, draw_date FROM session_draws WHERE session_id = 2 ORDER BY draw_number")
        draws = [dict(d) for d in cur.fetchall()]
        print(f"Loaded {len(draws)} draws.")
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
        return

    # Run Service
    service = CorrelationService(db_config)
    results = service.analyze_correlations(draws, 'mundo')
    
    print("\nCORRELATION RESULTS:")
    print(f"Total Rules Found: {results.get('rule_count', 0)}")
    
    top = results.get('top_correlations', [])
    for i, rule in enumerate(top[:10]):
        print(f"{i+1}. {rule['rule']} (Conf: {rule['confidence']}, Supp: {rule['support']})")

if __name__ == "__main__":
    verify_correlations()
