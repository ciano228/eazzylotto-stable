"""
Exploration automatique de la base de données PostgreSQL
"""

import sys
sys.path.append('backend')
from db_explorer_service import DatabaseExplorerService

def run_exploration():
    print("EXPLORATION AUTOMATIQUE DE LA BASE DE DONNEES")
    print("=" * 60)
    
    service = DatabaseExplorerService()
    
    # 1. Structure générale
    print("\n1. STRUCTURE GÉNÉRALE:")
    structure = service.explore_database_structure()
    
    if 'error' in structure:
        print(f"ERREUR connexion BD: {structure['error']}")
        return
    
    print(f"   Base: {structure['database']}")
    print(f"   Total tables: {structure['total_tables']}")
    print(f"   Tables sessions: {len(structure['session_related_tables'])}")
    print(f"   Tables tirages: {len(structure['draw_related_tables'])}")
    print(f"   Autres tables: {len(structure['other_tables'])}")
    
    if structure['session_related_tables']:
        print(f"   -> Sessions: {structure['session_related_tables']}")
    if structure['draw_related_tables']:
        print(f"   -> Tirages: {structure['draw_related_tables']}")
    
    # 2. Recherche sessions
    print("\n2. RECHERCHE SESSIONS:")
    sessions = service.search_session_data()
    
    if 'error' in sessions:
        print(f"ERREUR: {sessions['error']}")
    else:
        print(f"   Sessions trouvées: {sessions['sessions_found']}")
        if sessions['sessions_found']:
            for data in sessions['potential_session_data']:
                if 'error' not in data:
                    print(f"   [SESSION] {data['table']}: {data['columns']}")
    
    # 3. Recherche tirages
    print("\n3. RECHERCHE TIRAGES:")
    draws = service.search_draw_data()
    
    if 'error' in draws:
        print(f"ERREUR: {draws['error']}")
    else:
        print(f"   Tirages trouvés: {draws['draws_found']}")
        if draws['draws_found']:
            for data in draws['potential_draw_data']:
                if 'error' not in data:
                    print(f"   [TIRAGE] {data['table']}: {data['columns']}")
    
    # 4. Table combinations
    print("\n4. TABLE COMBINATIONS:")
    combinations = service.get_table_structure('combinations')
    
    if 'error' in combinations:
        print(f"ERREUR: {combinations['error']}")
    else:
        print(f"   Enregistrements: {combinations['record_count']}")
        print(f"   Colonnes: {[col['name'] for col in combinations['columns']]}")
    
    # 5. Toutes les tables
    print(f"\n5. TOUTES LES TABLES ({structure['total_tables']}):")
    for table in structure['tables']:
        print(f"   - {table}")

if __name__ == "__main__":
    run_exploration()