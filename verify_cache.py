import requests
import time
import json

BASE_URL = "http://localhost:8881/api/unified"

def test_cache(session_id, universe="mundo"):
    print(f"🚀 Testing cache for session {session_id} (universe: {universe})")
    
    # 1. Fetch draws for the session
    print(f"📥 Fetching draws for session {session_id}...")
    try:
        response = requests.get(f"{BASE_URL}/sessions/{session_id}/draws?limit=50")
        draws = response.json()
    except Exception as e:
        print(f"❌ Error fetching draws: {e}")
        return

    if not draws:
        print("⚠️ No draws found for this session.")
        return

    payload = {
        "session_id": session_id,
        "draws": draws,
        "universe": universe
    }

    # 2. First call (Uncached or filling cache)
    print("⏱️ First call (uncached)...")
    start_time = time.time()
    try:
        response1 = requests.post(f"{BASE_URL}/katula/analyze-session", json=payload)
        end_time = time.time()
        print(f"✅ First call took: {end_time - start_time:.4f} seconds")
    except Exception as e:
        print(f"❌ Error in first call: {e}")
        return

    # 3. Second call (Cached)
    print("⏱️ Second call (cached)...")
    start_time = time.time()
    try:
        response2 = requests.post(f"{BASE_URL}/katula/analyze-session", json=payload)
        end_time = time.time()
        print(f"✅ Second call took: {end_time - start_time:.4f} seconds")
    except Exception as e:
        print(f"❌ Error in second call: {e}")
        return

    # 4. Verify results equality
    res1 = response1.json()
    res2 = response2.json()
    
    # Compare structure and draw count
    if res1.get('status') == res2.get('status') and len(res1.get('analyzed_draws', [])) == len(res2.get('analyzed_draws', [])):
        print("✨ Results are consistent!")
    else:
        print("❌ Consistency check failed!")

if __name__ == "__main__":
    # Ensure server is running before starting this script
    # We use session 25 as requested
    test_cache(25)
