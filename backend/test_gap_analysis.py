#!/usr/bin/env python3
"""
Script de test pour l'analyse des écarts
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from app.services.gap_analysis_service import GapAnalysisService

def test_gap_analysis():
    """Test de l'analyse des écarts"""
    
    try:
        db = next(get_db())
        
        print("=== TEST ANALYSE DES ÉCARTS ===")
        print("🔍 Analyse en cours pour l'univers 'mundo'...")
        
        # Test du calcul des écarts
        gaps_data = GapAnalysisService.calculate_gaps(db, "mundo")
        
        print(f"\n📊 Attributs analysés: {list(gaps_data.keys())}")
        
        # Afficher un échantillon pour chaque type d'attribut
        for attr_type, values in gaps_data.items():
            print(f"\n--- {attr_type.upper()} ---")
            # Prendre les 3 premiers pour l'exemple
            sample_values = list(values.items())[:3]
            for value, stats in sample_values:
                print(f"  {value}:")
                print(f"    Écart actuel: {stats['current_gap']}")
                print(f"    Écart moyen: {stats['average_gap']}")
                print(f"    Écart max: {stats['max_gap']}")
                print(f"    Apparitions: {stats['total_appearances']}")
                print(f"    Régularité: {stats['regularity_score']}")
        
        print("\n=== TEST ATTRIBUTS EN RETARD ===")
        overdue = GapAnalysisService.get_overdue_attributes(db, "mundo")
        
        for attr_type, attributes in overdue.items():
            print(f"\n🔥 {attr_type.upper()} en retard:")
            for attr in attributes[:3]:  # Top 3
                print(f"  {attr['value']}: {attr['current_gap']} (moy: {attr['average_gap']}, ratio: {attr['delay_ratio']:.2f})")
        
        print("\n=== TEST ATTRIBUTS CHAUDS ===")
        hot = GapAnalysisService.get_hot_attributes(db, "mundo")
        
        for attr_type, attributes in hot.items():
            print(f"\n🌡️ {attr_type.upper()} chauds:")
            for attr in attributes[:3]:  # Top 3
                print(f"  {attr['value']}: {attr['current_gap']} (moy: {attr['average_gap']}, ratio: {attr['heat_ratio']:.2f})")
        
        print("\n=== RÉSUMÉ GÉNÉRAL ===")
        summary = GapAnalysisService.get_gaps_summary(db, "mundo")
        
        for attr_type, stats in summary.items():
            print(f"{attr_type}: {stats['total_values']} valeurs, écart moyen actuel: {stats['avg_current_gap']}")
        
        db.close()
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_gap_analysis()