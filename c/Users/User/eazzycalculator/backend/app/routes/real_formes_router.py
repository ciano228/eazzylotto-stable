"""
Router pour les formes réelles par univers - PostgreSQL
"""
from fastapi import APIRouter, HTTPException
from collections import defaultdict
import json
import sys
import os

# Import direct
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database_postgresql import get_postgres_connection

router = APIRouter()

@router.get("/formes/real/{universe}")
async def get_real_formes_by_universe(universe: str):
    """Récupérer les formes réelles pour un univers spécifique"""
    
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Requête pour les formes de cet univers (table par univers)
        query = f"""
        SELECT DISTINCT 
            forme,
            COUNT(*) as frequency
        FROM {universe} 
        WHERE forme IS NOT NULL 
        AND forme != ''
        GROUP BY forme
        ORDER BY frequency DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Aucune forme trouvée pour l'univers {universe}")
        
        # Organiser les formes
        formes_data = []
        simples = []
        composites = []
        
        for forme, frequency in results:
            forme_info = {
                'forme': forme,
                'frequency': frequency,
                'type': 'composite' if '-' in forme else 'simple'
            }
            formes_data.append(forme_info)
            
            if '-' in forme:
                composites.append(forme)
            else:
                simples.append(forme)
        
        conn.close()
        
        return {
            'universe': universe,
            'total_formes': len(formes_data),
            'formes': [f['forme'] for f in formes_data],
            'formes_with_frequency': formes_data,
            'simples': simples,
            'composites': composites,
            'geometry_type': 'composite' if len(composites) > len(simples) else 'mixed'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des formes: {str(e)}")

@router.get("/formes/real/all")
async def get_all_real_formes():
    """Récupérer toutes les formes réelles pour tous les univers"""
    
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Requête pour toutes les formes par univers
        query = """
        SELECT DISTINCT 
            univers,
            forme,
            COUNT(*) as frequency
        FROM katooling_main_system 
        WHERE forme IS NOT NULL 
        AND forme != ''
        GROUP BY univers, forme
        ORDER BY univers, frequency DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Organiser par univers
        universes_data = defaultdict(list)
        
        for univers, forme, frequency in results:
            universes_data[univers].append({
                'forme': forme,
                'frequency': frequency,
                'type': 'composite' if '-' in forme else 'simple'
            })
        
        # Formater la réponse
        output = {}
        for univers, formes_list in universes_data.items():
            simples = [f['forme'] for f in formes_list if f['type'] == 'simple']
            composites = [f['forme'] for f in formes_list if f['type'] == 'composite']
            
            output[univers] = {
                'total_formes': len(formes_list),
                'formes': [f['forme'] for f in formes_list],
                'formes_with_frequency': formes_list,
                'simples': simples,
                'composites': composites,
                'geometry_type': 'composite' if len(composites) > len(simples) else 'mixed'
            }
        
        conn.close()
        
        return {
            'total_universes': len(output),
            'universes': list(output.keys()),
            'data': output
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@router.get("/formes/real/{universe}/chip/{chip_number}")
async def get_real_chip_formes(universe: str, chip_number: int):
    """Récupérer les formes réelles pour un chip spécifique dans un univers"""
    
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Requête pour ce chip spécifique
        query = f"""
        SELECT 
            forme,
            denomination,
            COUNT(*) as frequency
        FROM {universe} 
        WHERE chip = %s
        AND forme IS NOT NULL 
        AND forme != ''
        GROUP BY forme, denomination
        ORDER BY frequency DESC
        """
        
        cursor.execute(query, (str(chip_number),))
        results = cursor.fetchall()
        
        if not results:
            return {
                'universe': universe,
                'chip': chip_number,
                'formes_data': {},
                'total_items': 0
            }
        
        # Organiser par forme
        formes_data = defaultdict(list)
        
        for forme, denomination, frequency in results:
            formes_data[forme].append({
                'denomination': denomination,
                'frequency': frequency
            })
        
        conn.close()
        
        return {
            'universe': universe,
            'chip': chip_number,
            'formes_data': dict(formes_data),
            'total_items': sum(len(items) for items in formes_data.values()),
            'available_formes': list(formes_data.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du chip: {str(e)}")