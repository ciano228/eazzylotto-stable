import httpx
import json

BASE_URL = "http://localhost:8000"
UNIVERSES = ["mundo", "fruity", "trigga", "roaster", "sunshine"]

def test_universe(universe):
    print(f"\n--- Testing Universe: {universe} ---")
    
    # 1. Test Gaps API
    print(f"Testing Gaps API for {universe}...")
    try:
        r = httpx.get(f"{BASE_URL}/api/analytics/gaps/{universe}")
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # Gaps structure might be empty if no data for that universe, but should be 200
            print(f"  Success: Received {len(data.get('gaps_analysis', {}))} attribute types.")
    except Exception as e:
        print(f"  Failed: {e}")

    # 2. Test Pattern Analysis for this universe
    print(f"Testing Pattern Analysis for {universe}...")
    try:
        payload = {
            "numbers": [1, 2, 3, 4, 5],
            "universe": universe,
            "threshold": 50
        }
        r = httpx.post(f"{BASE_URL}/api/patterns/analyze-draw", json=payload)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            print(f"  Success: Analysis returned {r.json().get('total_matches')} matches.")
    except Exception as e:
        print(f"  Failed: {e}")

if __name__ == "__main__":
    for u in UNIVERSES:
        test_universe(u)
