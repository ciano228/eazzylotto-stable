#!/usr/bin/env python3
"""
Test simple pour vérifier le service de patterns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.pattern_detection_service import PatternDetectionService
    print("✅ Import réussi!")
    
    from app.database.connection import get_db
    db = next(get_db())
    
    print("🔄 Test des cycles...")
    cycles = PatternDetectionService.detect_cycles(db, "mundo")
    print(f"Cycles trouvés: {len(cycles)}")
    
    print("✅ Test terminé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()