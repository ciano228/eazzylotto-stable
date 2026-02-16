import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.database.connection import get_db
from backend.app.services.pattern_recognition_service import PatternRecognitionService

def debug_similarity():
    # Target (Trigger)
    target_nums = [6, 80, 86, 82, 46]
    # Candidate (The one showing 100% match)
    candidate_nums = [12, 27, 64, 82, 86]
    
    universe = "mundo"
    
    print(f"--- Debugging Similarity ---")
    print(f"Target: {target_nums}")
    print(f"Candidate: {candidate_nums}")
    print(f"Universe: {universe}")
    
    service = PatternRecognitionService()
    
    # 1. Generate Signatures
    print("\n[1] Generating Signatures...")
    sig_target = service.generate_draw_signature(target_nums, universe)
    sig_candidate = service.generate_draw_signature(candidate_nums, universe)
    
    # 2. Compare using internal method
    print("\n[2] Comparing Signatures...")
    score, details = service._compare_signatures(sig_target, sig_candidate)
    
    print(f"\n[3] Result: Score = {score}%")
    print(f"Details: {details}")
    
    # 3. Deep Dive into attributes
    print("\n[4] Attribute Comparison Breakdown:")
    # Both signatures are lists of dicts (one per pair)
    # But usually we compare sets of (key, value)
    
    set_target = [service._attr_dict_to_set(p) for p in sig_target]
    set_candidate = [service._attr_dict_to_set(p) for p in sig_candidate]
    
    # We need to know how many "slots" matched
    # The logic in _compare_signatures sorts sets and compares them
    
    # Let's print the raw attributes for manual inspection
    print("\nTarget Attributes (per pair):")
    for i, pair in enumerate(sig_target):
        print(f"  Pair {i+1}: {pair}")

    print("\nCandidate Attributes (per pair):")
    for i, pair in enumerate(sig_candidate):
        print(f"  Pair {i+1}: {pair}")

if __name__ == "__main__":
    debug_similarity()
