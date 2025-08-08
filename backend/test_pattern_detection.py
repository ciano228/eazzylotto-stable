#!/usr/bin/env python3
"""
Script de test pour la détection de patterns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from app.services.pattern_detection_service import PatternDetectionService

def test_pattern_detection():
    """Test de la détection de patterns"""
    
    try:
        db = next(get_db())
        
        print("=== TEST DÉTECTION DE PATTERNS ===")
        print("🔍 Analyse en cours pour l'univers 'mundo'...")
        
        # Test de détection des cycles
        print("\n=== TEST CYCLES ===")
        cycles = PatternDetectionService.detect_cycles(db, "mundo")
        
        for attr_type, cycles_list in cycles.items():
            print(f"\n🔄 {attr_type.upper()} - Cycles détectés:")
            for cycle in cycles_list[:3]:  # Top 3
                print(f"  Pattern: {' -> '.join(cycle['pattern'])}")
                print(f"  Longueur: {cycle['cycle_length']}, Répétitions: {cycle['repetitions']}")
                print(f"  Force: {cycle['strength']}, Couverture: {cycle['coverage']}")
        
        # Test de détection des séquences
        print("\n=== TEST SÉQUENCES ===")
        sequences = PatternDetectionService.detect_sequences(db, "mundo")
        
        for attr_type, seq_list in sequences.items():
            print(f"\n🔗 {attr_type.upper()} - Séquences détectées:")
            for seq in seq_list[:3]:  # Top 3
                print(f"  {seq['from_value']} -> {seq['to_value']}")
                print(f"  Confiance: {seq['confidence']}, Support: {seq['support']}, Lift: {seq['lift']}")
        
        # Test de détection des associations
        print("\n=== TEST ASSOCIATIONS ===")
        associations = PatternDetectionService.find_associations(db, "mundo")
        
        for pair_name, assoc_list in associations.items():
            print(f"\n🤝 {pair_name.upper()} - Associations détectées:")
            for assoc in assoc_list[:2]:  # Top 2
                print(f"  {assoc['value1']} <-> {assoc['value2']}")
                print(f"  Lift: {assoc['lift']}, Support: {assoc['support']}")
                print(f"  Confiance1: {assoc['confidence1']}, Confiance2: {assoc['confidence2']}")
        
        # Test de détection des anomalies
        print("\n=== TEST ANOMALIES ===")
        anomalies = PatternDetectionService.detect_anomalies(db, "mundo")
        
        for attr_type, anom_list in anomalies.items():
            print(f"\n⚠️ {attr_type.upper()} - Anomalies détectées:")
            for anom in anom_list[:3]:  # Top 3
                print(f"  {anom['value']}: {anom['anomaly_type']}")
                print(f"  Taux récent: {anom['recent_rate']}, Taux historique: {anom['historical_rate']}")
                print(f"  Ratio de changement: {anom['change_ratio']}x")
        
        # Test du résumé complet
        print("\n=== RÉSUMÉ COMPLET ===")
        summary = PatternDetectionService.get_pattern_summary(db, "mundo")
        
        print(f"Cycles trouvés: {summary['cycles_found']}")
        print(f"Séquences trouvées: {summary['sequences_found']}")
        print(f"Associations trouvées: {summary['associations_found']}")
        print(f"Anomalies trouvées: {summary['anomalies_found']}")
        
        db.close()
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_pattern_detection()