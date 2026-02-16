#!/usr/bin/env python3
"""
Script de migration pour transférer les sessions du cache mémoire vers PostgreSQL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.migration_service import MigrationService
from backend.unified_session_service import UnifiedSessionService
from backend.postgres_session_service import PostgresSessionService

def main():
    print("=== MIGRATION SESSIONS VERS POSTGRESQL ===")
    
    # Initialiser les services
    migration_service = MigrationService()
    unified_service = UnifiedSessionService()
    postgres_service = PostgresSessionService()
    
    print("\n1. Vérification des sessions en mémoire...")
    
    # Initialiser session_test_001 si nécessaire
    session_data = unified_service.initialize_session_test_001()
    print(f"   ✓ session_test_001: {len(session_data['draws'])} tirages")
    
    # Lister toutes les sessions en mémoire
    all_sessions = unified_service.get_all_sessions()
    print(f"   ✓ Total sessions en mémoire: {len(all_sessions)}")
    
    print("\n2. Migration vers PostgreSQL...")
    
    # Migrer toutes les sessions
    results = migration_service.migrate_all_memory_sessions(unified_service)
    
    for session_id, success in results.items():
        status = "✓" if success else "✗"
        print(f"   {status} {session_id}: {'Migré' if success else 'Échec'}")
    
    print("\n3. Vérification PostgreSQL...")
    
    # Lister les sessions PostgreSQL
    postgres_sessions = postgres_service.list_sessions()
    print(f"   ✓ Sessions PostgreSQL: {len(postgres_sessions)}")
    
    for session in postgres_sessions:
        print(f"     - {session['session_id']}: {session['total_draws']} tirages")
    
    print("\n4. Test de récupération...")
    
    # Tester la récupération d'une session
    if postgres_sessions:
        test_session_id = postgres_sessions[0]['session_id']
        session_data = postgres_service.get_session(test_session_id)
        
        if session_data:
            print(f"   ✓ Test récupération {test_session_id}: OK")
            print(f"     - Nom: {session_data['name']}")
            print(f"     - Tirages: {len(session_data['draws'])}")
            
            # Statistiques
            stats = postgres_service.get_session_stats(test_session_id)
            print(f"     - Stats: {stats}")
        else:
            print(f"   ✗ Erreur récupération {test_session_id}")
    
    print("\n=== MIGRATION TERMINÉE ===")

if __name__ == "__main__":
    main()