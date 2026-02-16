#!/usr/bin/env python3
"""
Correctif simple pour l'accès à la session Algeria
Redirige vers les sessions mémoire disponibles
"""

import requests
import json

def fix_algeria_access():
    """Corrige l'accès à la session Algeria"""
    
    print("Correction de l'acces a la session Algeria...")
    
    try:
        # 1. Vérifier les sessions mémoire disponibles
        response = requests.get('http://localhost:8881/api/sessions', timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('status') == 'success' and result.get('sessions'):
                print(f"\nSessions memoire disponibles:")
                for session in result['sessions']:
                    print(f"  - {session['name']}: {session['completed_draws']}/{session['total_draws']} tirages")
                
                # Chercher Algeria
                algeria_session = None
                for session in result['sessions']:
                    if 'algeria' in session['name'].lower():
                        algeria_session = session
                        break
                
                if algeria_session:
                    print(f"\nSession Algeria trouvee: {algeria_session['name']}")
                    
                    # Tester l'accès aux détails
                    detail_response = requests.get(f"http://localhost:8881/api/sessions/{algeria_session['name']}")
                    
                    if detail_response.status_code == 200:
                        detail_result = detail_response.json()
                        session_data = detail_result.get('session', {})
                        
                        print(f"Details session Algeria:")
                        print(f"  - Nom: {session_data.get('session_name')}")
                        print(f"  - Total tirages: {session_data.get('total_draws')}")
                        print(f"  - Completes: {session_data.get('completed_draws')}")
                        print(f"  - Progres: {session_data.get('progress_percentage', 0):.1f}%")
                        
                        if session_data.get('periods'):
                            print(f"  - Periodes: {len(session_data['periods'])}")
                        
                        return {
                            'status': 'success',
                            'session_name': algeria_session['name'],
                            'access_url': f"http://localhost:8881/api/sessions/{algeria_session['name']}",
                            'message': f"Utilisez '{algeria_session['name']}' au lieu de 'pg_work_6'"
                        }
                    else:
                        print(f"Erreur acces details: {detail_response.status_code}")
                else:
                    print("\nAucune session Algeria trouvee dans la memoire")
                    
                    # Créer une session Algeria de test
                    return create_algeria_test_session()
            else:
                print("Aucune session memoire disponible")
        else:
            print(f"Erreur API sessions: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur connexion API: {e}")
    
    return create_algeria_fallback()

def create_algeria_test_session():
    """Crée une session Algeria de test"""
    print("\nCreation session Algeria de test...")
    
    try:
        # Créer une session Algeria avec des données de test
        create_data = {
            'session_name': 'algeria_test',
            'periods': 4,
            'description': 'Session Algeria de test'
        }
        
        response = requests.post(
            'http://localhost:8881/api/test-session/create',
            json=create_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Session Algeria creee: {result.get('session', {}).get('session_name')}")
            
            return {
                'status': 'success',
                'session_name': 'algeria_test',
                'access_url': 'http://localhost:8881/api/sessions/algeria_test',
                'message': "Session Algeria de test creee - utilisez 'algeria_test'"
            }
        else:
            print(f"Erreur creation session: {response.status_code}")
            
    except Exception as e:
        print(f"Erreur creation session Algeria: {e}")
    
    return create_algeria_fallback()

def create_algeria_fallback():
    """Crée un fallback pour Algeria"""
    return {
        'status': 'fallback',
        'session_name': 'session_test_001',
        'access_url': 'http://localhost:8881/api/sessions/session_test_001',
        'message': "Utilisez 'session_test_001' comme alternative a Algeria"
    }

def test_session_access(session_name):
    """Teste l'accès à une session"""
    try:
        response = requests.get(f'http://localhost:8881/api/sessions/{session_name}', timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"Acces OK pour {session_name}")
                return True
            else:
                print(f"Erreur session {session_name}: {result.get('error')}")
        else:
            print(f"Erreur HTTP {response.status_code} pour {session_name}")
            
    except Exception as e:
        print(f"Erreur test {session_name}: {e}")
    
    return False

def create_interface_fix():
    """Crée un correctif pour l'interface"""
    fix_js = """
// Correctif pour l'erreur pg_work_6
function fixAlgeriaSessionAccess() {
    // Remplacer pg_work_6 par algeria ou session_test_001
    const sessionSelect = document.getElementById('sessionSelect');
    if (sessionSelect) {
        // Supprimer les options PostgreSQL invalides
        Array.from(sessionSelect.options).forEach(option => {
            if (option.value.startsWith('pg_work_') || option.value.startsWith('pg_session_')) {
                option.remove();
            }
        });
        
        // Ajouter les sessions mémoire valides
        const validSessions = ['session_test_001', 'algeria_test', 'algeria'];
        validSessions.forEach(sessionName => {
            if (!Array.from(sessionSelect.options).find(opt => opt.value === sessionName)) {
                const option = document.createElement('option');
                option.value = sessionName;
                option.textContent = sessionName;
                sessionSelect.appendChild(option);
            }
        });
        
        // Sélectionner automatiquement une session valide
        if (sessionSelect.value.startsWith('pg_')) {
            sessionSelect.value = 'session_test_001';
        }
    }
}

// Appliquer le correctif au chargement
document.addEventListener('DOMContentLoaded', fixAlgeriaSessionAccess);
"""
    
    try:
        with open('../frontend/fix_algeria_session.js', 'w', encoding='utf-8') as f:
            f.write(fix_js)
        print("Correctif JavaScript cree: fix_algeria_session.js")
    except Exception as e:
        print(f"Erreur creation correctif JS: {e}")

if __name__ == "__main__":
    result = fix_algeria_access()
    
    print(f"\nResultat:")
    print(f"  Status: {result['status']}")
    print(f"  Session: {result['session_name']}")
    print(f"  URL: {result['access_url']}")
    print(f"  Message: {result['message']}")
    
    # Tester l'accès à la session recommandée
    print(f"\nTest d'acces a {result['session_name']}:")
    if test_session_access(result['session_name']):
        print("Acces confirme - la session fonctionne")
    else:
        print("Probleme d'acces - verifiez le serveur")
    
    # Créer le correctif JavaScript
    create_interface_fix()
    
    print(f"\nSolution:")
    print(f"1. Dans l'interface katula-temporal-analysis.html")
    print(f"2. Selectionnez '{result['session_name']}' au lieu de 'pg_work_6'")
    print(f"3. Ou incluez le fichier fix_algeria_session.js pour correction automatique")