"""
Script de test pour explorer la base de données PostgreSQL
"""

import asyncio
import aiohttp
import json

async def test_db_exploration():
    """Tester l'exploration de la BD"""
    
    base_url = "http://localhost:8881/api/db"
    
    async with aiohttp.ClientSession() as session:
        
        print("🔍 EXPLORATION DE LA BASE DE DONNÉES POSTGRESQL")
        print("=" * 60)
        
        # 1. Explorer la structure générale
        print("\n1. Structure générale de la BD:")
        try:
            async with session.get(f"{base_url}/explore") as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'success':
                        structure = data['database_structure']
                        print(f"   Base: {structure['database']}")
                        print(f"   Total tables: {structure['total_tables']}")
                        print(f"   Tables liées aux sessions: {len(structure['session_related_tables'])}")
                        print(f"   Tables liées aux tirages: {len(structure['draw_related_tables'])}")
                        
                        if structure['session_related_tables']:
                            print(f"   → Sessions: {structure['session_related_tables']}")
                        if structure['draw_related_tables']:
                            print(f"   → Tirages: {structure['draw_related_tables']}")
                    else:
                        print(f"   ❌ Erreur: {data['error']}")
                else:
                    print(f"   ❌ Erreur HTTP: {response.status}")
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
        
        # 2. Rechercher des sessions existantes
        print("\n2. Recherche de sessions existantes:")
        try:
            async with session.get(f"{base_url}/search-sessions") as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'success':
                        search = data['session_search']
                        print(f"   Sessions trouvées: {search['sessions_found']}")
                        
                        if search['sessions_found']:
                            print(f"   Tables de sessions: {search['session_tables']}")
                            
                            for session_data in search['potential_session_data']:
                                if 'error' not in session_data:
                                    print(f"\n   📋 Table: {session_data['table']}")
                                    print(f"      Colonnes: {session_data['columns']}")
                                    if session_data['sample_data']:
                                        print(f"      Exemples: {len(session_data['sample_data'])} enregistrements")
                        else:
                            print("   ❌ Aucune table de session trouvée")
                    else:
                        print(f"   ❌ Erreur: {data['error']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 3. Rechercher des tirages existants
        print("\n3. Recherche de tirages existants:")
        try:
            async with session.get(f"{base_url}/search-draws") as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'success':
                        search = data['draw_search']
                        print(f"   Tirages trouvés: {search['draws_found']}")
                        
                        if search['draws_found']:
                            print(f"   Tables de tirages: {search['draw_tables']}")
                            
                            for draw_data in search['potential_draw_data']:
                                if 'error' not in draw_data:
                                    print(f"\n   🎲 Table: {draw_data['table']}")
                                    print(f"      Colonnes: {draw_data['columns']}")
                                    if draw_data['sample_data']:
                                        print(f"      Exemples: {len(draw_data['sample_data'])} enregistrements")
                        else:
                            print("   ❌ Aucune table de tirage trouvée")
                    else:
                        print(f"   ❌ Erreur: {data['error']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 4. Explorer la table combinations (connue)
        print("\n4. Structure de la table 'combinations':")
        try:
            async with session.get(f"{base_url}/table/combinations") as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'success':
                        table = data['table_structure']
                        print(f"   Table: {table['table_name']}")
                        print(f"   Enregistrements: {table['record_count']}")
                        print(f"   Colonnes ({len(table['columns'])}):")
                        
                        for col in table['columns']:
                            nullable = "NULL" if col['nullable'] else "NOT NULL"
                            print(f"      - {col['name']}: {col['type']} {nullable}")
                        
                        if table['constraints']:
                            print(f"   Contraintes:")
                            for constraint in table['constraints']:
                                print(f"      - {constraint['type']}: {constraint['column']}")
                    else:
                        print(f"   ❌ Erreur: {data['error']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_exploration())