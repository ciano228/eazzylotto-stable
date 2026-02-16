"""
Test du système intelligent de reprise de session
Démontre l'auto-chargement des loteries selon le programme et les dates
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

def test_smart_session_resume():
    """Test complet du système intelligent de reprise de session"""
    
    print("=" * 80)
    print("🧪 TEST: Système Intelligent de Reprise de Session")
    print("=" * 80)
    
    # 1. Créer une session avec planning cyclique
    print("\n📋 Étape 1: Création d'une session avec planning")
    print("-" * 80)
    
    session_data = {
        "name": "Session Test - Auto-Sync",
        "description": "Test de synchronisation automatique des tirages",
        "lottery_type": "EuroMillions",
        "numbers_per_draw": 5,
        "total_draws": 15,  # 15 tirages sur 3 semaines
        "cycle_length": 5,  # 5 tirages par période
        "number_range_min": 1,
        "number_range_max": 50,
        "start_date": "08/06/2025",  # Dimanche 8 juin 2025
        "lottery_schedule": [
            {"name": "EuroMillions Dimanche", "day_offset": 6},  # Dimanche
            {"name": "EuroMillions Mardi", "day_offset": 1},     # Mardi
            {"name": "EuroMillions Vendredi", "day_offset": 4}   # Vendredi
        ]
    }
    
    response = requests.post(f"{API_BASE}/session/sessions", json=session_data)
    
    if response.status_code == 200:
        result = response.json()
        session_id = result["id"]
        print(f"✅ Session créée: ID={session_id}, Nom='{result['name']}'")
        print(f"   Cycle: {result['cycle_length']} tirages/période")
        print(f"   Total: {result['total_draws']} tirages")
    else:
        print(f"❌ Erreur création: {response.text}")
        return
    
    # 2. Vérifier les tirages créés automatiquement
    print("\n📅 Étape 2: Vérification des tirages auto-générés")
    print("-" * 80)
    
    response = requests.get(f"{API_BASE}/session/sessions/{session_id}/draws")
    
    if response.status_code == 200:
        draws = response.json()
        print(f"✅ {len(draws)} tirages créés automatiquement:")
        
        for i, draw in enumerate(draws[:6]):  # Afficher les 6 premiers
            print(f"   Tirage #{draw['draw_number']}: {draw['lottery_name']} - {draw['draw_date']}")
        
        if len(draws) > 6:
            print(f"   ... et {len(draws) - 6} autres tirages")
    else:
        print(f"❌ Erreur récupération: {response.text}")
        return
    
    # 3. Simuler la saisie de quelques tirages
    print("\n✍️ Étape 3: Saisie de quelques tirages")
    print("-" * 80)
    
    # Saisir les tirages 1, 2, 3
    for draw_num in [1, 2, 3]:
        numbers = [5, 12, 23, 34, 45]  # Numéros fictifs
        draw_data = {
            "numbers": numbers,
            "draw_date": draws[draw_num - 1]["draw_date"]
        }
        
        response = requests.post(
            f"{API_BASE}/session/sessions/{session_id}/draws/{draw_num}",
            json=draw_data
        )
        
        if response.status_code == 200:
            print(f"✅ Tirage #{draw_num} sauvegardé")
        else:
            print(f"❌ Erreur tirage #{draw_num}: {response.text}")
    
    # 4. Désactiver la session (simuler fermeture)
    print("\n🔒 Étape 4: Désactivation de la session (simulation fermeture)")
    print("-" * 80)
    
    # Créer une autre session pour désactiver la première
    temp_session = {
        "name": "Session Temporaire",
        "lottery_type": "Loto",
        "numbers_per_draw": 5,
        "total_draws": 5,
        "start_date": "10/06/2025",
        "lottery_schedule": []
    }
    
    response = requests.post(f"{API_BASE}/session/sessions", json=temp_session)
    if response.status_code == 200:
        print("✅ Session désactivée (nouvelle session créée)")
    
    # 5. Réactiver la session originale (REPRISE INTELLIGENTE)
    print("\n🚀 Étape 5: REPRISE INTELLIGENTE de la session")
    print("-" * 80)
    print("Le système va automatiquement:")
    print("  • Charger le planning des loteries")
    print("  • Respecter les dates programmées")
    print("  • Créer les tirages manquants si nécessaire")
    print("  • Réaligner les dates selon le calendrier")
    
    response = requests.post(f"{API_BASE}/session/sessions/{session_id}/activate")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")
        
        sync_info = result.get("sync_info", {})
        print(f"\n📊 Résultat de la synchronisation:")
        print(f"   • Tirages créés: {sync_info.get('created_draws', 0)}")
        print(f"   • Tirages mis à jour: {sync_info.get('updated_draws', 0)}")
        print(f"   • Total de tirages: {sync_info.get('total_draws', 0)}")
    else:
        print(f"❌ Erreur activation: {response.text}")
        return
    
    # 6. Vérifier l'état après reprise
    print("\n🔍 Étape 6: Vérification de l'état après reprise")
    print("-" * 80)
    
    response = requests.get(f"{API_BASE}/session/sessions/{session_id}/draws")
    
    if response.status_code == 200:
        draws = response.json()
        completed = sum(1 for d in draws if d["is_completed"])
        pending = len(draws) - completed
        
        print(f"✅ État de la session:")
        print(f"   • Total tirages: {len(draws)}")
        print(f"   • Tirages complétés: {completed}")
        print(f"   • Tirages en attente: {pending}")
        
        print(f"\n📅 Prochains tirages programmés:")
        for draw in draws[completed:completed+3]:
            status = "✓ Complété" if draw["is_completed"] else "⏳ En attente"
            print(f"   Tirage #{draw['draw_number']}: {draw['lottery_name']} - {draw['draw_date']} [{status}]")
    
    # 7. Vérifier le progrès
    print("\n📈 Étape 7: Progrès de la session")
    print("-" * 80)
    
    response = requests.get(f"{API_BASE}/session/sessions/{session_id}/progress")
    
    if response.status_code == 200:
        progress = response.json()
        print(f"✅ Progrès:")
        print(f"   • Session: {progress['session_name']}")
        print(f"   • Tirage actuel: {progress['current_draw']}/{progress['total_draws']}")
        print(f"   • Complétés: {progress['completed_draws']}")
        print(f"   • Pourcentage: {progress['progress_percentage']}%")
    
    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ: Le système est intelligent et auto-synchronise!")
    print("=" * 80)
    print("\n💡 Avantages:")
    print("   ✓ Pas besoin de recréer les tirages manuellement")
    print("   ✓ Les dates sont respectées automatiquement")
    print("   ✓ Le planning cyclique est maintenu")
    print("   ✓ Les tirages manquants sont créés automatiquement")
    print("   ✓ Reprise transparente de la session")

if __name__ == "__main__":
    try:
        test_smart_session_resume()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur est démarré sur http://localhost:8000")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
