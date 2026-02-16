"""
Script de Test: Poids Structurels Katula
Valide le calcul des cardinalités, probabilités et gaps attendus
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_structural_weights():
    """Test complet du système de poids structurels"""
    
    print("=" * 80)
    print("🧪 TEST: Système de Poids Structurels Katula")
    print("=" * 80)
    
    # Test 1: Récupérer le poids d'un chip spécifique
    print("\n📊 Test 1: Poids Structurel d'un Chip")
    print("-" * 80)
    
    response = requests.get(
        f"{API_BASE}/structural-weights/mundo/chip/chip_5"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chip 5 (Mundo):")
        print(f"   Cardinalité: {data['cardinality']} combinaisons")
        print(f"   Total Mundo: {data['total_universe']} combinaisons")
        print(f"   Probabilité: {data['probability']:.6f} ({data['probability']*100:.2f}%)")
        print(f"   Gap Attendu: {data['expected_gap']:.2f} tirages")
        print(f"   Poids: {data['weight']:.6f}")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    # Test 2: Récupérer tous les poids pour les lignes
    print("\n📊 Test 2: Poids de Toutes les Lignes (Mundo)")
    print("-" * 80)
    
    response = requests.get(
        f"{API_BASE}/structural-weights/mundo/ligne"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} lignes trouvées:")
        for ligne, info in sorted(data.items())[:3]:  # Afficher les 3 premières
            print(f"   {ligne}: {info['cardinality']} combos, "
                  f"P={info['probability']:.4f}, "
                  f"Gap={info['expected_gap']:.2f}")
        if len(data) > 3:
            print(f"   ... et {len(data) - 3} autres lignes")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    # Test 3: Statistiques globales d'un univers
    print("\n📊 Test 3: Statistiques Globales (Mundo)")
    print("-" * 80)
    
    response = requests.get(
        f"{API_BASE}/structural-weights/mundo/statistics"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Univers: {data['universe']}")
        print(f"   Total combinaisons: {data['total_combinations']}")
        print(f"   Attributs:")
        for attr_type, attr_data in data['attributes'].items():
            print(f"      {attr_type}: {attr_data['count']} valeurs distinctes")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    # Test 4: Calcul de score de gap
    print("\n📊 Test 4: Score de Gap Normalisé")
    print("-" * 80)
    
    test_cases = [
        {"gap": 40, "chip": "chip_5", "desc": "Chip 5 avec gap de 40"},
        {"gap": 10, "chip": "chip_5", "desc": "Chip 5 avec gap de 10"},
        {"gap": 80, "chip": "chip_5", "desc": "Chip 5 avec gap de 80"}
    ]
    
    for case in test_cases:
        response = requests.get(
            f"{API_BASE}/structural-weights/gap-score",
            params={
                "current_gap": case["gap"],
                "universe": "mundo",
                "attribute_type": "chip",
                "attribute_value": case["chip"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {case['desc']}:")
            print(f"   Gap actuel: {data['current_gap']}")
            print(f"   Gap attendu: {data['expected_gap']}")
            print(f"   Score: {data['gap_score']} → {data['interpretation']}")
        else:
            print(f"❌ Erreur pour {case['desc']}: {response.status_code}")
    
    # Test 5: Prédiction d'apparition
    print("\n📊 Test 5: Prédiction d'Apparition")
    print("-" * 80)
    
    response = requests.get(
        f"{API_BASE}/structural-weights/predict-appearance",
        params={
            "current_gap": 40,
            "n_draws": 10,
            "universe": "mundo",
            "attribute_type": "chip",
            "attribute_value": "chip_5"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Prédiction pour Chip 5:")
        print(f"   Gap actuel: {data['current_gap']} tirages")
        print(f"   Horizon: {data['n_draws']} tirages")
        print(f"   Probabilité d'apparition: {data['percentage']}")
        print(f"   Gap attendu: {data['expected_gap']} tirages")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    # Test 6: Cardinalité simple
    print("\n📊 Test 6: Cardinalité d'un Élément")
    print("-" * 80)
    
    elements = [
        ("chip", "chip_5", "Chip 5"),
        ("ligne", "ligne1", "Ligne 1"),
        ("forme", "carre", "Forme Carré")
    ]
    
    for attr_type, attr_value, desc in elements:
        response = requests.get(
            f"{API_BASE}/structural-weights/cardinality",
            params={
                "universe": "mundo",
                "attribute_type": attr_type,
                "attribute_value": attr_value
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {desc}:")
            print(f"   Cardinalité: {data['cardinality']}/{data['total_universe']} ({data['percentage']})")
        else:
            print(f"❌ Erreur pour {desc}: {response.status_code}")
    
    # Test 7: Comparaison entre univers
    print("\n📊 Test 7: Comparaison Entre Univers")
    print("-" * 80)
    
    universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    for universe in universes:
        response = requests.get(
            f"{API_BASE}/structural-weights/{universe}/chip/chip_5"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chip 5 dans {universe.capitalize()}:")
            print(f"   {data['cardinality']}/{data['total_universe']} combos, "
                  f"P={data['probability']:.4f}, "
                  f"Gap={data['expected_gap']:.2f}")
        else:
            print(f"⚠️ {universe.capitalize()}: Données non disponibles")
    
    # Test 8: Validation mathématique
    print("\n📊 Test 8: Validation Mathématique")
    print("-" * 80)
    
    response = requests.get(f"{API_BASE}/structural-weights/mundo/ligne")
    
    if response.status_code == 200:
        data = response.json()
        total_prob = sum(info['probability'] for info in data.values())
        print(f"✅ Somme des probabilités (lignes): {total_prob:.6f}")
        if abs(total_prob - 1.0) < 0.01:
            print(f"   ✓ Validation OK (≈ 1.0)")
        else:
            print(f"   ⚠️ Attention: devrait être ≈ 1.0")
    
    print("\n" + "=" * 80)
    print("✅ TESTS TERMINÉS")
    print("=" * 80)
    
    print("\n💡 Utilisation:")
    print("   • Les poids structurels sont maintenant disponibles via l'API")
    print("   • Utilisez-les pour calculer des gaps normalisés")
    print("   • Intégrez-les dans vos analyses statistiques")
    print("   • Comparez équitablement des éléments de tailles différentes")


if __name__ == "__main__":
    try:
        test_structural_weights()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur est démarré sur http://localhost:8000")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
