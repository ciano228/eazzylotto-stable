import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    print("Starting Endpoint Verification...")
    
    with TestClient(app) as client:
        # Debug: Print all registered routes
        print("\n[DEBUG] Registered Routes:")
        for route in app.routes:
            methods = ",".join(route.methods) if hasattr(route, "methods") else "None"
            path = getattr(route, "path", getattr(route, "path_format", "Unknown"))
            print(f"  {path} [{methods}]")
        print("[DEBUG] End Routes\n")

        # 0. Test Health Endpoint (Sanity Check)
        print("\n0. Testing GET /api/health...")
        try:
            response = client.get("/api/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Success! Health check passed.")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")

        # 1. Test Gaps Endpoint

        print("\n1. Testing GET /api/analytics/gaps/mundo...")
        try:
            response = client.get("/api/analytics/gaps/mundo")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Success! Got {len(data.get('gaps_analysis', {}))} items in gaps_analysis.")
                print(f"   Overdue attributes detected: {len(data.get('overdue_attributes', {}))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")

        # 2. Test Sessions List Endpoint
        print("\n2. Testing GET /api/session/sessions...")
        try:
            response = client.get("/api/session/sessions")
            # In main.py we registered ("app.routes.unified_session", "/api", ["sessions"])
            # and unified_session.py has @router.get("/session/sessions")
            # So path is /api/session/sessions
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                sessions = data.get('sessions', [])
                print(f"   Success! Found {len(sessions)} sessions.")
            else:
                 print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")

        # 3. Test Pattern Analysis (POST)
        print("\n3. Testing POST /api/patterns/analyze-draw...")
        try:
            payload = {
                "numbers": [1, 2, 3, 4, 5], 
                "universe": "mundo",
                "threshold": 50
            }
            response = client.post("/api/patterns/analyze-draw", json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Success! Analysis complete. Matches found: {len(data.get('matches', []))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")

if __name__ == "__main__":
    test_endpoints()
