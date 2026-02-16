
import requests
import sys

BASE_URL = "http://localhost:8881"

def test_auto_load():
    print("🚀 Démarrage du test auto-pilote des statistiques avancées...")
    
    # 1. Récupérer les sessions
    try:
        print(f"📡 Récupération des sessions depuis {BASE_URL}/api/unified/session/sessions...")
        resp = requests.get(f"{BASE_URL}/api/unified/session/sessions")
        resp.raise_for_status()
        response_data = resp.json()
        sessions = response_data.get('sessions')
        
        if not sessions:
            print("❌ Aucune session trouvée dans la réponse de l'API. Impossible de tester.")
            return
            
        print(f"✅ {len(sessions)} sessions trouvées.")
        
        # Prendre la première session (la plus récente normalement)
        target_session = sessions[0]
        session_id = target_session['id']
        session_name = target_session.get('name', 'Sans nom')
        print(f"🎯 Session cible: {session_name} (ID: {session_id})")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions: {e}")
        return

    # 2. Tester le chargement des stats pour cette session
    try:
        print(f"📡 Chargement des stats pour la session {session_id}...")
        # Note: On ne force pas le paramètre universe, pour tester la détection auto, 
        # mais le frontend envoie potentiellement ?universe=... si détecté.
        # Le script frontend corrigé envoie ?universe=... seulement si trouvé dans le DOM.
        # On va tester SANS paramètre universe pour voir si le backend se débrouille (ce qui était le point critique).
        
        stats_url = f"{BASE_URL}/api/stats/advanced/{session_id}"
        print(f"   GET {stats_url}")
        
        stats_resp = requests.get(stats_url)
        stats_resp.raise_for_status()
        data = stats_resp.json()
        
        if data.get('status') == 'success':
            stats = data.get('stats', {})
            total_draws = data.get('total_draws', 0)
            universe = data.get('universe')
            
            print(f"✅ Succès! Stats récupérées pour l'univers '{universe}'.")
            print(f"📊 Nombre de tirages analysés: {total_draws}")
            
            if not stats:
                print("⚠️  Avertissement: L'objet 'stats' est vide. Le backend a répondu succès mais sans données calculées.")
                print("   Causes possibles: Pas de mapping pour cet univers, ou tirages vides.")
            else:
                print("📈 Aperçu des données reçues:")
                for key in ['forme', 'tome', 'granque', 'petique']:
                    items = stats.get(key, [])
                    print(f"   - {key.capitalize()}: {len(items)} éléments trouvés")
                    if items:
                        top = max(items, key=lambda x: x['count'])
                        print(f"     Top: {top['value']} (Sorties: {top['count']}, Écart: {top['due']})")
                
                if total_draws > 0 and stats:
                    print("\n🎉 TEST RÉUSSI: Les statistiques sont générées correctement.")
                else:
                    print("\n⚠️  TEST MITIGÉ: Réponse OK mais données potentiellement incomplètes.")
                    
        else:
            print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur lors du chargement des stats: {e}")

if __name__ == "__main__":
    try:
        test_auto_load()
    except KeyboardInterrupt:
        print("\nTest interrompu.")
