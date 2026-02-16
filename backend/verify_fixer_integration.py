
import requests
import json
import time
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if needed
SESSION_MAPPING_FILE = "session_mapping.json" # Assumed to be in working dir or backend root

def get_mapping_mtime():
    """Get modification time of session_mapping.json"""
    # Try different locations
    paths = [
        "session_mapping.json",
        "backend/session_mapping.json",
        "../session_mapping.json",
        "c:/Users/User/eazzycalculator/backend/session_mapping.json"
    ]
    
    for path in paths:
        if os.path.exists(path):
            return os.path.getmtime(path), path
            
    return None, None

def test_create_session(route_type="unified"):
    """
    Test session creation and check if fixer ran.
    route_type: 'unified' or 'standard'
    """
    print(f"\n--- Testing Session Creation ({route_type}) ---")
    
    # 1. Get current mtime of mapping file
    initial_mtime, mapping_path = get_mapping_mtime()
    if mapping_path:
        print(f"Found mapping file at: {mapping_path}")
        print(f"Initial mtime: {initial_mtime}")
    else:
        print("Warning: session_mapping.json not found before test. It should be created.")

    # 2. Create Session
    session_name = f"AutoTest_{int(time.time())}"
    payload = {
        "name": session_name,
        "description": "Automated verification test",
        "lottery_type": "mundo",
        "numbers_per_draw": 5,
        "total_draws": 10,
        "lottery_schedule": [],
        "start_date": "01/01/2026",
        "number_range_min": 1,
        "number_range_max": 90
    }
    
    url = ""
    if route_type == "unified":
        url = f"{BASE_URL}/api/unified/session"
    else:
        url = f"{BASE_URL}/api/session/sessions" # Adjust based on actual router prefix
        # Note: standard session_service might be under different endpoint, checking check unified_session.py and session.py
    
    # Rereading routes to confirm URL structure.
    # unified_session.py -> @router.post("/session") -> likely /api/unified/session if mounted under /api/unified
    # session.py -> @router.post("/sessions") -> likely /api/session/sessions if mounted under /api/session
    
    # Let's assume standard ports/prefixes. 
    # If this fails, we will debug URLs.
    
    try:
        # Try finding the correct URL for "standard"
        if route_type == "standard":
             url = f"{BASE_URL}/api/sessions" # Common convention
        
        print(f"Sending POST to {url}...")
        response = requests.post(url, json=payload)
        
        if response.status_code not in [200, 201]:
            print(f"Failed to create session. Status: {response.status_code}")
            print(response.text)
            return False
            
        print("Session created successfully.")
        
        # 3. Wait a moment then check mtime
        time.sleep(2) # Give it a moment if it's async or slow
        
        final_mtime, _ = get_mapping_mtime()
        
        if not final_mtime:
             print("Error: session_mapping.json still not found.")
             return False
             
        if mapping_path:
            if final_mtime > initial_mtime:
                print("SUCCESS: session_mapping.json was updated.")
                return True
            else:
                print(f"FAILURE: session_mapping.json was NOT updated. (Initial: {initial_mtime}, Final: {final_mtime})")
                return False
        else:
            print("session_mapping.json was created new.")
            return True

    except Exception as e:
        print(f"Exception during test: {e}")
        return False

if __name__ == "__main__":
    # Test passed arguments or default
    if len(sys.argv) > 1:
        test_create_session(sys.argv[1])
    else:
        # Default test unified
        test_create_session("unified")
