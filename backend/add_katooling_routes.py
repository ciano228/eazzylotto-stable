#!/usr/bin/env python3
"""
Ajouter les routes katooling au serveur simple
"""

from katooling_session_service import KatoolingSessionService

def add_katooling_routes(app):
    """Ajouter les routes pour accéder aux sessions katooling"""
    
    service = KatoolingSessionService()
    
    @app.route('/api/katooling/sessions', methods=['GET'])
    def get_katooling_sessions():
        """Récupérer toutes les sessions katooling"""
        try:
            result = service.get_all_sessions()
            return result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @app.route('/api/katooling/sessions/<session_id>', methods=['GET'])
    def get_katooling_session_details(session_id):
        """Récupérer les détails d'une session katooling"""
        try:
            result = service.get_session_details(session_id)
            return result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @app.route('/api/katooling/algeria', methods=['GET'])
    def get_algeria_sessions():
        """Récupérer spécifiquement les sessions Algeria"""
        try:
            result = service.get_algeria_sessions()
            return result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @app.route('/api/katooling/session-mapping', methods=['GET'])
    def get_session_mapping():
        """Récupérer le mapping des sessions pour l'interface"""
        try:
            all_sessions = service.get_all_sessions()
            
            if all_sessions['status'] != 'success':
                return all_sessions
            
            # Créer un mapping pour l'interface
            mapping = {}
            for session in all_sessions['sessions']:
                # Mapping pour compatibilité avec l'ancienne interface
                if session['name'] == 'algeria':
                    mapping[f"pg_work_{session['real_id']}"] = {
                        'real_id': session['id'],
                        'name': session['name'],
                        'type': session['type'],
                        'access_url': f"/api/katooling/sessions/{session['id']}",
                        'draws': session['actual_draws']
                    }
                
                # Mapping direct
                mapping[session['id']] = {
                    'real_id': session['real_id'],
                    'name': session['name'],
                    'type': session['type'],
                    'access_url': f"/api/katooling/sessions/{session['id']}",
                    'draws': session['actual_draws']
                }
            
            return {
                'status': 'success',
                'mapping': mapping,
                'total_sessions': len(mapping)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Test des routes
if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    add_katooling_routes(app)
    
    print("Test des routes katooling...")
    
    with app.test_client() as client:
        # Test sessions
        response = client.get('/api/katooling/sessions')
        print(f"Sessions: {response.status_code}")
        
        # Test Algeria
        response = client.get('/api/katooling/algeria')
        print(f"Algeria: {response.status_code}")
        
        # Test mapping
        response = client.get('/api/katooling/session-mapping')
        print(f"Mapping: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            if data['status'] == 'success':
                print("Mapping disponible:")
                for key, value in data['mapping'].items():
                    if 'algeria' in value['name'].lower():
                        print(f"  {key} -> {value['name']} ({value['draws']} tirages)")
    
    print("Routes katooling prêtes à être intégrées")