import requests
import json
import sys

def test_chat():
    url = "http://localhost:8881/api/chat/message"
    
    payload = {
        "message": "analyse cette prediction",
        "context": {
            "prediction_id": 1, # Mock ID
            "universe": "mundo"
        }
    }
    
    print(f"Testing POST {url}...")
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        except:
            print("Raw Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_chat()
