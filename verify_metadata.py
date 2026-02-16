import httpx
import json

BASE_URL = "http://localhost:8000"

def verify_metadata():
    print("Verifying Metadata in Twin Draws...")
    payload = {
        "numbers": [1, 2, 3, 4, 5],
        "universe": "mundo",
        "threshold": 50
    }
    try:
        r = httpx.post(f"{BASE_URL}/api/patterns/analyze-draw", json=payload)
        if r.status_code == 200:
            data = r.json()
            matches = data.get("matches", [])
            if matches:
                 m = matches[0]
                 print(f"Match 0: Date={m.get('draw_date')}, Numbers={m.get('draw_numbers')}")
                 print(f"  Session: {m.get('session_name')}")
                 print(f"  Lottery: {m.get('lottery_name')}")
                 
                 if m.get('session_name') and m.get('lottery_name'):
                     print("\n✅ Verification SUCCESS: Metadata is present!")
                 else:
                     print("\n❌ Verification FAILED: Metadata missing or empty.")
            else:
                print("No matches found to verify.")
        else:
            print(f"API Error: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def verify_fallback():
    print("\nVerifying Fallback Logic for Rare Signatures...")
    # Use a likely "rare" set of numbers or just verify consequence structure
    payload = {
        "numbers": [10, 20, 30, 40, 50], # Might be rare in some universes
        "universe": "mundo",
        "threshold": 30 # Allow low matches to trigger fallback
    }
    r = httpx.post(f"{BASE_URL}/api/patterns/analyze-draw", json=payload)
    if r.status_code == 200:
        data = r.json()
        matches = data.get("matches", [])
        best_score = max([m['match_score'] for m in matches]) if matches else 0
        print(f"  Best Match Score found: {best_score}%")
        
        cons = data.get("consequences", {})
        if cons.get("most_frequent_numbers"):
            print(f"✅ Fallback SUCCESS: Predictions found ({len(cons['most_frequent_numbers'])} numbers)")
        else:
            print(f"⚠️ Note: Predictions still empty. Threshold was {30 if best_score < 50 else (50 if best_score < 80 else 80)}%")
    else:
        print(f"❌ API Error: {r.status_code}")

if __name__ == "__main__":
    verify_metadata()
    verify_fallback()
