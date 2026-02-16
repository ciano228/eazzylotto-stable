
import sys
import os
import json
from datetime import datetime

# Adjust path to include the current directory
sys.path.append(os.getcwd())

from backend.session_statistics_engine import SessionStatisticsEngine
from backend.unified_db_session_service import UnifiedDBSessionService

db_config = {
    'dbname': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'host': 'localhost',
    'port': '5432'
}

def verify_synthetic_stats():
    print(f"\n{'='*60}")
    print(f"VERIFICATION: SYNTHETIC ATTRIBUTES IN STATS")
    print(f"{'='*60}\n")
    
    # 1. Initialize Engines
    stats_engine = SessionStatisticsEngine(db_config)
    session_service = UnifiedDBSessionService()
    
    # 2. Get draws from a real session (e.g., Session 1 or the simulation session 25)
    session_id = 25 # The 10-year simulation we created
    print(f"Loading draws for session {session_id}...")
    draws = session_service.get_session_draws(session_id)
    
    if not draws:
        print("Error: No draws found for session 25.")
        return
        
    print(f"Analyzed {len(draws)} draws.")
    
    # 3. Calculate Stats
    print("Calculating statistics including synthetic attributes...")
    start_time = datetime.now()
    report = stats_engine.calculate_stats(draws, universe='mundo')
    end_time = datetime.now()
    
    print(f"Calculation completed in {end_time - start_time}.")
    
    # 4. Check for synthetic attribute keys
    # Synthetic keys are like 'forme_rectangle_tome_tome1'
    synthetic_keys = [k for k in report.keys() if '_' in k and any(attr in k for attr in ['forme', 'tome', 'granque', 'engine'])]
    
    print(f"\nSynthetic attribute types found: {len(synthetic_keys)}")
    
    # Sort by frequency of the first value to find interesting ones
    top_synthetics = []
    for sk in synthetic_keys:
        if report[sk]:
            top_val = max(report[sk], key=lambda x: x['frequency'])
            top_synthetics.append((sk, top_val['value'], top_val['frequency'], top_val['count']))
            
    top_synthetics.sort(key=lambda x: x[2], reverse=True)
    
    print("\nTop 10 Synthetic Patterns in Stats:")
    for i, (sk, val, freq, count) in enumerate(top_synthetics[:10], 1):
        print(f"{i:2}. {sk:40} : {val:20} -> {freq:5.2f}% ({count} hits)")
        
    # Specifically check for rectangle_tome1
    target_key = "forme_rectangle_tome_tome1"
    if target_key in report:
        print(f"\nTarget found: {target_key}")
        for entry in report[target_key]:
            print(f"  - Value: {entry['value']}, Frequency: {entry['frequency']}%, Count: {entry['count']}")

if __name__ == "__main__":
    verify_synthetic_stats()
