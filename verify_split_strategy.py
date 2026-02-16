
import sys
import os
import json
from datetime import datetime

# Adjust path to include the current directory
sys.path.append(os.getcwd())

from backend.split_strategy_service import SplitStrategyService

db_config = {
    'dbname': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'host': 'localhost',
    'port': '5432'
}

def verify_split_strategy():
    print(f"\n{'='*60}")
    print(f"VERIFICATION: SPLIT STRATEGY")
    print(f"{'='*60}\n")
    
    split_service = SplitStrategyService(db_config)
    
    universe = 'mundo'
    session_id = 25 # Simulation session
    
    # Test with normal attribute: granque:Q1
    print("Test 1: Normal Attribute (granque:Q1)")
    result1 = split_service.perform_split(universe, session_id, 'granque', 'Q1', lookback_days=180)
    
    if result1['status'] == 'success':
        print(f"  Total Combos: {result1['total_count']}")
        print(f"  YA-PLAYED: {result1['ya_played']['count']} combos (Profit Potential: {result1['ya_played']['profit_potential']})")
        print(f"  NOT-YET-PLAYED: {result1['not_yet_played']['count']} combos (Profit Potential: {result1['not_yet_played']['profit_potential']})")
    else:
        print(f"  Error: {result1['message']}")
        
    print("\n" + "-"*40 + "\n")
    
    # Test with synthetic: forme_tome:rectangle_tome1
    print("Test 2: Synthetic Attribute (forme_tome:rectangle_tome1)")
    # Note: the attribute_name used here matches how the SyntheticAttributeEngine names them
    result2 = split_service.perform_split(universe, session_id, 'forme_tome', 'rectangle_tome1', lookback_days=180)
    
    if result2['status'] == 'success':
        print(f"  Total Combos: {result2['total_count']}")
        print(f"  YA-PLAYED: {result2['ya_played']['count']} combos (Profit Potential: {result2['ya_played']['profit_potential']})")
        print(f"  NOT-YET-PLAYED: {result2['not_yet_played']['count']} combos (Profit Potential: {result2['not_yet_played']['profit_potential']})")
        
        # Check if profit potential is actually better
        if result2['ya_played']['profit_potential'] > (200 - result2['total_count']):
            print(f"\n  ✅ SUCCESS: YA-PLAYED subset is MORE profitable (+{result2['ya_played']['profit_potential']}) than full zone ({200 - result2['total_count']})")
    else:
        print(f"  Error: {result2['message']}")

if __name__ == "__main__":
    verify_split_strategy()
