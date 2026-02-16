"""
Verification script for Win-Tracker session-specific endpoints
Tests that session filtering works correctly
"""
import requests
import json

API_BASE = "http://localhost:8881"

def test_win_tracker_with_session():
    print("=" * 80)
    print("TESTING WIN-TRACKER WITH SESSION FILTERING")
    print("=" * 80)
    
    # Test 1: Opportunities for specific session
    print("\n1. Testing opportunities endpoint WITH session_id=24...")
    response = requests.get(f"{API_BASE}/win-tracker/opportunities/mundo?session_id=24&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Session ID: {data.get('session_id')}")
        print(f"   Opportunities found: {len(data.get('opportunities', []))}")
        
        if data.get('opportunities'):
            print("\n   Top Opportunity:")
            opp = data['opportunities'][0]
            print(f"   - Zone: {opp.get('zone_type')} = {opp.get('zone_value')}")
            print(f"   - Investment: {opp.get('investment_cost')} units")
            print(f"   - Expected Profit: {opp.get('expected_profit')}")
            print(f"   - Expected ROI: {opp.get('expected_roi')}%")
            print(f"   - Recommendation: {opp.get('recommendation')}")
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
    
    # Test 2: Opportunities without session (global)
    print("\n2. Testing opportunities endpoint WITHOUT session_id (global)...")
    response = requests.get(f"{API_BASE}/win-tracker/opportunities/mundo?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Session ID: {data.get('session_id')} (should be None)")
        print(f"   Opportunities found: {len(data.get('opportunities', []))}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: Specific zone analysis with session
    print("\n3. Testing zone analysis WITH session_id=24...")
    response = requests.get(f"{API_BASE}/win-tracker/analyze/mundo/petique/q1?session_id=24")
    if response.status_code == 200:
        data = response.json()
        analysis = data.get('analysis', {})
        print(f"   Zone: {analysis.get('zone_type')} = {analysis.get('zone_value')}")
        print(f"   Total Combinations: {analysis.get('total_combinations')}")
        print(f"   Investment Cost: {analysis.get('investment_cost')}")
        print(f"   Estimated Probability: {analysis.get('estimated_probability')}")
        print(f"   Expected ROI: {analysis.get('expected_roi')}%")
        print(f"   Recommendation: {analysis.get('recommendation')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Statistics with session
    print("\n4. Testing statistics WITH session_id=24...")
    response = requests.get(f"{API_BASE}/win-tracker/statistics/mundo?session_id=24")
    if response.status_code == 200:
        data = response.json()
        stats = data.get('statistics', {})
        print(f"   Total Zones: {stats.get('total_zones')}")
        print(f"   Profitable Zones: {stats.get('profitable_zones')}")
        print(f"   BUY Recommendations: {stats.get('buy_recommendations')}")
        print(f"   Average ROI: {stats.get('average_roi', 0):.2f}%")
        print(f"   Best ROI: {stats.get('best_roi', 0):.2f}%")
    else:
        print(f"   ERROR: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_win_tracker_with_session()
