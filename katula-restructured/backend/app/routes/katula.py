"""
Routeur pour les fonctionnalités spécifiques de l'application Katula.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from ..database.connection import get_db_cursor
from ..database.models import ReponseAPI
from ..utils.validators import validate_universe, validate_chip_number

router = APIRouter()

@router.get("/universes/{universe}/table", response_model=ReponseAPI)
async def get_katula_table(
    universe: str,
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de résultats à retourner"),
    offset: int = Query(0, ge=0, description="Nombre d'éléments à sauter")
):
    """
    Récupère les données de la table Katula pour un univers donné avec pagination.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Requête pour récupérer les données avec pagination
            query = """
                SELECT *
                FROM {}
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """.format(universe)
            
            cursor.execute(query, (limit, offset))
            resultats = cursor.fetchall()
            
            # Comptage total (pour la pagination)
            count_query = "SELECT COUNT(*) as total FROM {}".format(universe)
            cursor.execute(count_query)
            total = cursor.fetchone()['total']
            
            # Formatage de la réponse
            return ReponseAPI.succes(
                donnees={
                    'univers': universe,
                    'donnees': resultats,
                    'pagination': {
                        'total': total,
                        'limit': limit,
                        'offset': offset,
                        'has_more': (offset + len(resultats)) < total
                    }
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données de la table: {str(e)}"
        )

@router.get("/universes/{universe}/quadruples", response_model=ReponseAPI)
async def get_quadruples(
    universe: str,
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum de quadruples à retourner")
):
    """
    Récupère les quadruples les plus fréquents pour un univers donné.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Requête pour récupérer les quadruples les plus fréquents
            query = """
                WITH quadruples AS (
                    SELECT 
                        LEAST(forme1, forme2, forme3, forme4) as f1,
                        GREATEST(
                            GREATEST(forme1, forme2, forme3, forme4),
                            GREATEST(forme1, forme2, forme4, forme3),
                            GREATEST(forme1, forme3, forme2, forme4),
                            GREATEST(forme1, forme3, forme4, forme2),
                            GREATEST(forme1, forme4, forme2, forme3),
                            GREATEST(forme1, forme4, forme3, forme2),
                            GREATEST(forme2, forme1, forme3, forme4),
                            GREATEST(forme2, forme1, forme4, forme3),
                            GREATEST(forme2, forme3, forme1, forme4),
                            GREATEST(forme2, forme3, forme4, forme1),
                            GREATEST(forme2, forme4, forme1, forme3),
                            GREATEST(forme2, forme4, forme3, forme1),
                            GREATEST(forme3, forme1, forme2, forme4),
                            GREATEST(forme3, forme1, forme4, forme2),
                            GREATEST(forme3, forme2, forme1, forme4),
                            GREATEST(forme3, forme2, forme4, forme1),
                            GREATEST(forme3, forme4, forme1, forme2),
                            GREATEST(forme3, forme4, forme2, forme1),
                            GREATEST(forme4, forme1, forme2, forme3),
                            GREATEST(forme4, forme1, forme3, forme2),
                            GREATEST(forme4, forme2, forme1, forme3),
                            GREATEST(forme4, forme2, forme3, forme1),
                            GREATEST(forme4, forme3, forme1, forme2),
                            GREATEST(forme4, forme3, forme2, forme1)
                        ) as f4,
                        ARRAY[
                            LEAST(forme1, forme2, forme3, forme4),
                            LEAST(
                                GREATEST(LEAST(forme1, forme2), LEAST(forme3, forme4)),
                                GREATEST(LEAST(forme1, forme3), LEAST(forme2, forme4)),
                                GREATEST(LEAST(forme1, forme4), LEAST(forme2, forme3))
                            ),
                            GREATEST(
                                LEAST(GREATEST(forme1, forme2), GREATEST(forme3, forme4)),
                                LEAST(GREATEST(forme1, forme3), GREATEST(forme2, forme4)),
                                LEAST(GREATEST(forme1, forme4), GREATEST(forme2, forme3))
                            ),
                            GREATEST(forme1, forme2, forme3, forme4)
                        ] as formes_ordonnees,
                        COUNT(*) as frequence
                    FROM {}
                    WHERE forma1 IS NOT NULL AND forma2 IS NOT NULL AND 
                          forma3 IS NOT NULL AND forma4 IS NOT NULL
                    GROUP BY f1, f4, formes_ordonnees
                    HAVING COUNT(*) > 1
                    ORDER BY frequence DESC
                    LIMIT %s
                )
                SELECT 
                    formes_ordonnees,
                    frequence,
                    (SELECT COUNT(*) FROM quadruples) as total_quadruples
                FROM quadruples
            """.format(universe)
            
            cursor.execute(query, (limit,))
            resultats = cursor.fetchall()
            
            if not resultats:
                return ReponseAPI.succes(
                    donnees={
                        'univers': universe,
                        'quadruples': [],
                        'total': 0,
                        'message': 'Aucun quadruple trouvé pour cet univers.'
                    }
                )
            
            total_quadruples = resultats[0]['total_quadruples'] if resultats else 0
            
            # Formatage des résultats
            quadruples = []
            for row in resultats:
                quadruples.append({
                    'formes': row['formes_ordonnees'],
                    'frequence': row['frequence']
                })
            
            return ReponseAPI.succes(
                donnees={
                    'univers': universe,
                    'quadruples': quadruples,
                    'total': total_quadruples,
                    'limit': limit
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des quadruples: {str(e)}"
        )

@router.get("/universes/{universe}/stats", response_model=ReponseAPI)
async def get_universe_stats(universe: str):
    """
    Récupère les statistiques globales pour un univers donné.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Nombre total d'entrées
            cursor.execute(f"SELECT COUNT(*) as total FROM {universe}")
            total_entrees = cursor.fetchone()['total']
            
            # Nombre de formes uniques
            cursor.execute("""
                SELECT COUNT(DISTINCT forme) as total_formes 
                FROM {}
                WHERE forme IS NOT NULL AND forme != ''
            """.format(universe))
            total_formes = cursor.fetchone()['total_formes']
            
            # Nombre de formes simples et composites
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT CASE WHEN forme NOT LIKE '%%-%%' THEN forme END) as formes_simples,
                    COUNT(DISTINCT CASE WHEN forme LIKE '%%-%%' THEN forme END) as formes_composites
                FROM {}
                WHERE forme IS NOT NULL AND forme != ''
            """.format(universe))
            formes_stats = cursor.fetchone()
            
            # Dernière mise à jour
            cursor.execute("""
                SELECT MAX(created_at) as derniere_maj 
                FROM {}
            """.format(universe))
            derniere_maj = cursor.fetchone()['derniere_maj']
            
            # Création de la réponse
            stats = {
                'univers': universe,
                'total_entrees': total_entrees,
                'total_formes': total_formes,
                'formes_simples': formes_stats['formes_simples'],
                'formes_composites': formes_stats['formes_composites'],
                'derniere_maj': derniere_maj.isoformat() if derniere_maj else None,
                'chips': []
            }
            
            # Statistiques par chip
            cursor.execute("""
                SELECT 
                    chip,
                    COUNT(*) as total_formes,
                    COUNT(DISTINCT forme) as formes_uniques,
                    MAX(created_at) as derniere_observation
                FROM {}
                WHERE forme IS NOT NULL AND forme != ''
                GROUP BY chip
                ORDER BY chip
            """.format(universe))
            
            for row in cursor.fetchall():
                stats['chips'].append({
                    'chip': row['chip'],
                    'total_formes': row['total_formes'],
                    'formes_uniques': row['formes_uniques'],
                    'derniere_observation': row['derniere_observation'].isoformat() if row['derniere_observation'] else None
                })
            
            return ReponseAPI.succes(donnees=stats)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )
