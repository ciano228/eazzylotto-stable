def simulate_filtering(journal_entries, universe):
    """Simule la logique de filtrage implémentée dans unified_session.py"""
    all_entries = journal_entries
    
    # 1. Chercher les entrées valides pour l'univers demandé
    universe_entries = [e for e in all_entries if e.get("univers") == universe and e.get("status") == "normal"]
    
    if universe_entries:
        return universe_entries
    else:
        return [{
            "status": "no_hold",
            "univers": universe,
            "combination_str": "NO-HOLD"
        }]

def test_filtering():
    print("--- Verifying No-Hold Filtering Logic ---")
    
    # Case 1: Valid combinations exist for the universe
    print("\nCase 1: Valid Mundo combinations exist among others")
    mock_entries = [
        {"univers": "mundo", "status": "normal", "combination_str": "65-76"},
        {"univers": "fruity", "status": "normal", "combination_str": "12-34"},
        {"status": "no_hold", "univers": "N/A"} # Typical JournalService artifact
    ]
    result = simulate_filtering(mock_entries, "mundo")
    print(f"Result count: {len(result)}")
    for r in result:
        print(f"  - {r.get('combination_str')} ({r.get('univers')} / {r.get('status')})")
        
    if len(result) == 1 and result[0]["combination_str"] == "65-76":
        print("✅ PASS: Correct valid entries returned.")
    else:
        print("❌ FAIL: Redundant entries or wrong priorities.")

    # Case 2: No combinations exist for the universe
    print("\nCase 2: No Mundo combinations exist")
    mock_entries = [
        {"univers": "fruity", "status": "normal", "combination_str": "10-20"},
        {"status": "no_hold", "univers": "N/A"},
        {"status": "no_hold", "univers": "N/A"}
    ]
    result = simulate_filtering(mock_entries, "mundo")
    print(f"Result count: {len(result)}")
    for r in result:
        print(f"  - {r.get('combination_str')} ({r.get('univers')} / {r.get('status')})")
        
    if len(result) == 1 and result[0]["status"] == "no_hold" and result[0]["univers"] == "mundo":
        print("✅ PASS: Single No-Hold placeholder returned.")
    else:
        print("❌ FAIL: Multiple placeholders or incorrect status.")

if __name__ == "__main__":
    test_filtering()
