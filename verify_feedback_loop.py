import httpx
import json
import time

BASE_URL = "http://localhost:8000"

def test_feedback_loop():
    print("🧪 Testing Prediction Feedback Loop...")

    # 1. Record a prediction
    print("Step 1: Recording a mock prediction...")
    payload = {
        "universe": "mundo",
        "trigger_numbers": [1, 2, 3, 4, 5],
        "predicted_numbers": [{"number": 10, "frequency": 50}, {"number": 20, "frequency": 40}],
        "predicted_pairs": ["10-20"],
        "predicted_attributes": {"Engine": "E1"}
    }
    r = httpx.post(f"{BASE_URL}/api/performance/record", json=payload)
    if r.status_code != 200:
        print(f"❌ Failed to record: {r.text}")
        return
    print("✅ Prediction recorded.")

    # 2. Get stats (should find no evaluated data yet)
    print("Step 2: Checking stats (empty expected)...")
    r = httpx.get(f"{BASE_URL}/api/performance/stats?universe=mundo")
    print(f"Stats: {r.json()}")

    # 3. Simulate adding a real draw that "follows" the prediction
    # Since we use 'now()' as prediction_date, we need to add a draw with a later date.
    # We'll just wait a second and use a fresh timestamp if we were doing absolute dates, 
    # but the service uses DB query draw_date > prediction_date.
    
    # Note: In our system 'session_draws' reflects history. 
    # To truly test evaluation, we'd need to insert a draw into session_draws via SQL or API.
    # Let's check if there is an endpoint to add draws.
    
if __name__ == "__main__":
    test_feedback_loop()
