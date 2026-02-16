import sys
import os

# Ajouter le chemin du backend pour l'import (ajuster selon la structure réelle si nécessaire)
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.journal_service_v2 import JournalServiceV2
import json

def verify_fix():
    print("--- Verifying JournalServiceV2 Correlation Fix ---")
    
    # Test 1: Order stored in DB (assuming 65-76 is stored as confirmed by previous check)
    print("\nTest 1: Input (65, 76) - Should succeed")
    entry1 = JournalServiceV2.generate_journal_entry(65, 76)
    if "error" in entry1:
        print(f"❌ Failed: {entry1['error']}")
    else:
        print(f"✅ Success: Found {entry1['combination_str']} ({entry1['univers']}/{entry1['num1_analysis']['forme']})")

    # Test 2: Reversed order (76, 65) - Was failing before fix
    print("\nTest 2: Input (76, 65) - Should now succeed")
    entry2 = JournalServiceV2.generate_journal_entry(76, 65)
    if "error" in entry2:
        print(f"❌ Failed: {entry2['error']}")
    else:
        print(f"✅ Success: Found {entry2['combination_str']} ({entry2['univers']}/{entry2['num1_analysis']['forme']})")
        
    # Test 3: String inputs
    print("\nTest 3: Input ('76', '65') - Should now succeed")
    entry3 = JournalServiceV2.generate_journal_entry("76", "65")
    if "error" in entry3:
        print(f"❌ Failed: {entry3['error']}")
    else:
        print(f"✅ Success: Found {entry3['combination_str']} ({entry3['univers']}/{entry3['num1_analysis']['forme']})")

    # Compare results
    if entry1.get("combination_id") == entry2.get("combination_id") == entry3.get("combination_id") and entry1.get("combination_id") is not None:
        print("\n🏆 FIX VERIFIED: All input variants return the same combination ID.")
    else:
        print("\n❌ VERIFICATION FAILED: Results differ or IDs not found.")

if __name__ == "__main__":
    verify_fix()
