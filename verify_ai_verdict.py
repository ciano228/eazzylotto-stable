import httpx
import json

BASE_URL = "http://localhost:8000"

def verify_ai_verdict():
    print("🤖 Testing AI VERDICT Engine (Fusion)...")

    payload = {
        "numbers": [4, 5, 13, 24, 60], # Trigger draw
        "universe": "mundo"
    }
    
    try:
        r = httpx.post(f"{BASE_URL}/api/verdict/analyze", json=payload, timeout=20.0)
        if r.status_code == 200:
            data = r.json()
            print("✅ Verdict generated successfully!")
            print(f"  Confidence: {data['confidence_score']}%")
            print(f"  Top Verdict Numbers: {[n['number'] for n in data['top_verdict_numbers'][:5]]}")
            print(f"  Scenarios Analyzed: {data['sources']['pattern_recognition']['events_analyzed']}")
            
            if data['confidence_score'] > 0 and len(data['top_verdict_numbers']) > 0:
                print("\n🏆 Verification SUCCESS: AI Engine is healthy and producing results.")
            else:
                print("\n⚠️ Note: Engine produced empty/zero results (check database content).")
        else:
            print(f"❌ API Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    verify_ai_verdict()
