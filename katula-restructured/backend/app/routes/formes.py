"""
Routeur pour la gestion des formes dans les différents univers.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from ..database.connection import get_db_cursor
from ..database.models import (
    FormeBase, FormeAvecFrequence, UniversFormes, ReponseAPI
)
from ..utils.validators import validate_universe, get_forme_icon, get_forme_color

router = APIRouter()

@router.get("/universes/{universe}", response_model=ReponseAPI)
async def get_univers_formes(
    universe: str,
    include_inactive: bool = Query(False, description="Inclure les formes inactives")
):
    """
    Récupère toutes les formes disponibles pour un univers donné avec leurs fréquences.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Requête pour récupérer les formes et leurs fréquences
            query = """
                SELECT 
                    forme,
                    COUNT(*) as frequence,
                    CASE WHEN forme LIKE '%-%' THEN 'composite' ELSE 'simple' END as type
                FROM {}
                WHERE forme IS NOT NULL AND forme != ''
                GROUP BY forme
                ORDER BY frequence DESC
            """.format(universe)
            
            cursor.execute(query)
            resultats = cursor.fetchall()
            
            # Traitement des résultats
            formes = []
            formes_simples = []
            formes_composites = []
            
            for row in resultats:
                forme_nom = row['forme']
                forme_type = row['type']
                
                forme = FormeAvecFrequence(
                    nom=forme_nom,
                    type=forme_type,
                    frequence=row['frequence'],
                    icone=get_forme_icon(forme_nom),
                    couleur=get_forme_color(forme_nom)
                )
                
                formes.append(forme)
                
                if forme_type == 'simple':
                    formes_simples.append(forme_nom)
                else:
                    formes_composites.append(forme_nom)
            
            # Création de la réponse
            reponse = UniversFormes(
                univers=universe,
                formes=formes,
                total_formes=len(formes),
                formes_simples=formes_simples,
                formes_composites=formes_composites
            )
            
            return ReponseAPI.succes(donnees=reponse.dict())
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des formes: {str(e)}"
        )

@router.get("/{forme}/chips", response_model=ReponseAPI)
async def get_chips_by_forme(
    forme: str,
    universe: str = Query(..., description="Nom de l'univers"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de résultats à retourner"),
    offset: int = Query(0, ge=0, description="Nombre d'éléments à sauter")
):
    """
    Récupère tous les chips contenant une forme spécifique dans un univers donné.
    """
    try:
        # Validation des paramètres
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Requête pour récupérer les chips contenant la forme
            query = """
                SELECT 
                    chip,
                    denomination,
                    COUNT(*) as frequence
                FROM {}
                WHERE forme = %s
                GROUP BY chip, denomination
                ORDER BY frequence DESC
                LIMIT %s OFFSET %s
            """.format(universe)
            
            cursor.execute(query, (forme, limit, offset))
            resultats = cursor.fetchall()
            
            # Comptage total (pour la pagination)
            count_query = """
                SELECT COUNT(DISTINCT chip) as total
                FROM {}
                WHERE forme = %s
            """.format(universe)
            
            cursor.execute(count_query, (forme,))
            total = cursor.fetchone()['total']
            
            # Formatage de la réponse
            chips = [
                {
                    'chip': row['chip'],
                    'denomination': row['denomination'] or 'Non spécifiée',
                    'frequence': row['frequence']
                }
                for row in resultats
            ]
            
            return ReponseAPI.succes(
                donnees={
                    'forme': forme,
                    'univers': universe,
                    'total': total,
                    'chips': chips,
                    'pagination': {
                        'limit': limit,
                        'offset': offset,
                        'has_more': (offset + len(chips)) < total
                    }
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des chips: {str(e)}"
        )

@router.get("/universes/{universe}/chip/{chip_number}", response_model=ReponseAPI)
async def get_chip_formes(
    universe: str,
    chip_number: int
):
    """
    Récupère toutes les formes d'un chip spécifique dans un univers donné.
    """
    try:
        # Validation des paramètres
        universe = validate_universe(universe)
        chip_number = validate_chip_number(chip_number)
        
        with get_db_cursor() as cursor:
            # Vérifier si le chip existe dans l'univers
            check_query = """
                SELECT EXISTS(
                    SELECT 1 FROM {} 
                    WHERE chip = %s 
                    LIMIT 1
                ) as exists
            """.format(universe)
            
            cursor.execute(check_query, (f"chip{chip_number}",))
            exists = cursor.fetchone()['exists']
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Le chip {chip_number} n'existe pas dans l'univers {universe}"
                )
            
            # Récupérer les formes du chip
            query = """
                SELECT 
                    forme,
                    denomination,
                    COUNT(*) as frequence
                FROM {}
                WHERE chip = %s
                GROUP BY forme, denomination
                ORDER BY frequence DESC
            """.format(universe)
            
            cursor.execute(query, (f"chip{chip_number}",))
            resultats = cursor.fetchall()
            
            # Traitement des résultats
            formes = []
            for row in resultats:
                forme_nom = row['forme']
                
                forme = {
                    'forme': forme_nom,
                    'denomination': row['denomination'] or 'Non spécifiée',
                    'frequence': row['frequence'],
                    'icone': get_forme_icon(forme_nom),
                    'couleur': get_forme_color(forme_nom)
                }
                formes.append(forme)
            
            # Création de la réponse
            reponse = {
                'univers': universe,
                'chip': chip_number,
                'formes': formes,
                'total_formes': len(formes)
            }
            
            return ReponseAPI.succes(donnees=reponse)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des formes du chip: {str(e)}"
        )
