"""
Test Rapide du Service Katula Corrigé
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_service():
    try:
        print("=== TEST SERVICE KATULA CORRIGÉ ===")
        
        # Test 1: Import du service
        print("1. Import du service...")
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        print("OK Service importe avec succes")
        
        # Test 2: Configuration DB
        print("2. Vérification configuration DB...")
        print(f"   DB Config: {service.db_config}")
        
        # Test 3: Test connexion simple
        print("3. Test connexion PostgreSQL...")
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM combinations")
        total = cursor.fetchone()[0]
        print(f"OK Connexion - {total} lignes dans combinations")
        cursor.close()
        conn.close()
        
        # Test 4: Test service avec mundo
        print("4. Test service get_katula_table(mundo)...")
        result = service.get_katula_table('mundo')
        
        if 'error' in result:
            print(f"ERREUR: {result['error']}")
            return False
        
        print(f"OK Service - Source: {result.get('source', 'N/A')}")
        print(f"   Univers: {result.get('universe', 'N/A')}")
        print(f"   Chips: {result.get('total_chips', 'N/A')}")
        print(f"   Statut: {result.get('status', 'N/A')}")
        
        # Test 5: Vérifier que ça utilise bien combinations
        uses_combinations = result.get('source') == 'combinations'
        print(f"   Utilise table combinations: {'OUI' if uses_combinations else 'NON'}")
        
        return uses_combinations
        
    except Exception as e:
        print(f"ERREUR lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_service()
    print(f"\n=== RESULTAT: {'SUCCES' if success else 'ECHEC'} ===")