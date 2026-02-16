"""
Debug de la requête SQL
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_query():
    try:
        print("=== DEBUG REQUÊTE SQL ===")
        
        import psycopg2
        from backend.katula_complete_service import KatulaCompleteService
        
        service = KatulaCompleteService()
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
        # Test 1: Structure de la table combinations
        print("1. Structure table combinations:")
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'combinations' ORDER BY ordinal_position")
        columns = cursor.fetchall()
        for col in columns[:10]:  # Premières 10 colonnes
            print(f"   {col[0]}: {col[1]}")
        
        # Test 2: Échantillon de données
        print("\n2. Échantillon données combinations:")
        cursor.execute("SELECT chip, forme, denomination, univers FROM combinations WHERE univers = 'mundo' LIMIT 5")
        sample = cursor.fetchall()
        for row in sample:
            print(f"   chip={row[0]}, forme={row[1]}, denomination={row[2]}, univers={row[3]}")
        
        # Test 3: Test de la requête problématique
        print("\n3. Test requête corrigée:")
        query = """
            SELECT 
                CASE 
                    WHEN chip ~ '^[0-9]+$' THEN CAST(chip AS INTEGER)
                    WHEN chip LIKE 'chip%' THEN CAST(REPLACE(chip, 'chip', '') AS INTEGER)
                    ELSE 1
                END as chip_id,
                forme,
                STRING_AGG(DISTINCT denomination, '/') as denominations,
                petique,
                tome,
                granque_name
            FROM combinations
            WHERE univers = %s AND chip IS NOT NULL
            GROUP BY chip, forme, petique, tome, granque_name
            ORDER BY chip_id, forme
            LIMIT 5
        """
        
        cursor.execute(query, ('mundo',))
        results = cursor.fetchall()
        print(f"   Résultats: {len(results)} lignes")
        for row in results:
            print(f"   {row}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_query()