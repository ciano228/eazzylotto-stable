
import requests
import json
import sys

BASE_URL = "http://localhost:8881/api"
UNIVERSE = "mundo"

def test_correlations():
    print(f"Testing Correlations for {UNIVERSE}...")
    try:
        url = f"{BASE_URL}/analytics/correlations/{UNIVERSE}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
            return
            
        data = response.json()
        if data.get('status') == 'success':
            rules = data.get('data', {}).get('top_correlations', [])
            print(f"SUCCESS: Found {len(rules)} correlation rules.")
            if rules:
                print(f"Sample Rule: {rules[0]}")
        else:
            print(f"FAILED: Response status not success: {data}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_predictions():
    print(f"\nTesting Predictions for {UNIVERSE}...")
    try:
        url = f"{BASE_URL}/analytics/predict/next/{UNIVERSE}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
            return
            
        data = response.json()
        if data.get('status') == 'success':
            preds = data.get('predictions', {})
            print(f"SUCCESS: Predictions received for keys: {list(preds.keys())}")
            
            for key, val in preds.items():
                status = val.get('status', 'unknown')
                print(f"  - {key}: {status}")
                if 'predictions' in val and val['predictions']:
                    print(f"    Top: {val['predictions'][0]}")
        else:
            print(f"FAILED: Response status not success: {data}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_correlations()
    test_predictions()
