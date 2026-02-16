import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.services.verdict_engine_service import VerdictEngineService
from backend.app.database.connection import SessionLocal

def test_verdict():
    print("--- Testing Verdict Engine ---")
    db = SessionLocal()
    numbers = [22, 54, 61, 89, 29]
    universe = "mundo"
    
    try:
        print(f"Launching verdict for {numbers} in {universe}...")
        result = VerdictEngineService.get_unified_verdict(db, numbers, universe)
        print("Success! Result keys:", result.keys())
        print("Confidence Score:", result.get("confidence_score"))
        print("Top Numbers:", [n['number'] for n in result.get("top_verdict_numbers", [])])
    except Exception as e:
        print(f"FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_verdict()
