"""
Routeur pour les données formatées spécifiquement pour l'interface utilisateur.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from ..database.connection import get_db_cursor
from ..database.models import ReponseAPI, ChipDetails, UniversChips
from ..utils.validators import validate_universe, validate_chip_number, get_forme_icon, get_forme_color

router = APIRouter()

@router.get("/universes/{universe}/chip-details", response_model=ReponseAPI)
async def get_chip_details(
    universe: str,
    chip_number: Optional[int] = Query(None, description="Numéro du chip (1-48)")
):
    """
    Récupère les détails des chips pour un univers donné, avec option de filtre par numéro de chip.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Construction de la requête en fonction des paramètres
            query_params = []
            where_clause = ""
            
            if chip_number is not None:
                chip_number = validate_chip_number(chip_number)
                where_clause = "WHERE chip = %s"
                query_params.append(f"chip{chip_number}")
            
            # Requête pour récupérer les données des chips
            query = f"""
                WITH formes_chip AS (
                    SELECT 
                        chip,
                        forme,
                        denomination,
                        COUNT(*) as frequence,
                        MAX(created_at) as derniere_observation
                    FROM {universe}
                    {where_clause}
                    GROUP BY chip, forme, denomination
                )
                SELECT 
                    chip,
                    jsonb_agg(
                        jsonb_build_object(
                            'forme', forme,
                            'denomination', COALESCE(denomination, 'Non spécifiée'),
                            'frequence', frequence,
                            'derniere_observation', derniere_observation,
                            'icone', %s,
                            'couleur', %s
                        )
                    ) as formes_data
                FROM formes_chip
                GROUP BY chip
                ORDER BY chip
            """
            
            # Exécution de la requête avec les paramètres
            cursor.execute(query, (get_forme_icon(''), get_forme_color('')))
            resultats = cursor.fetchall()
            
            # Traitement des résultats
            chips = {}
            for row in resultats:
                # Extraction du numéro de chip
                chip_num = int(row['chip'].replace('chip', ''))
                
                # Mise à jour des icônes et couleurs pour chaque forme
                for forme_data in row['formes_data']:
                    forme_nom = forme_data['forme']
                    forme_data['icone'] = get_forme_icon(forme_nom)
                    forme_data['couleur'] = get_forme_color(forme_nom)
                
                chips[chip_num] = {
                    'formes_data': row['formes_data']
                }
            
            # Création de la réponse
            reponse = {
                'univers': universe,
                'chips': chips,
                'total_chips': len(chips)
            }
            
            if chip_number is not None and not chips:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Aucune donnée trouvée pour le chip {chip_number} dans l'univers {universe}"
                )
            
            return ReponseAPI.succes(donnees=reponse)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des détails des chips: {str(e)}"
        )

@router.get("/universes/{universe}/drawer-data", response_model=ReponseAPI)
async def get_drawer_data(universe: str):
    """
    Récupère les données nécessaires pour l'affichage des tiroirs dans l'interface utilisateur.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Récupération des formes avec leurs fréquences
            query_formes = f"""
                SELECT 
                    forme,
                    COUNT(*) as frequence,
                    CASE WHEN forme LIKE '%-%' THEN 'composite' ELSE 'simple' END as type
                FROM {universe}
                WHERE forme IS NOT NULL AND forme != ''
                GROUP BY forme
                ORDER BY frequence DESC
            """
            
            cursor.execute(query_formes)
            formes = cursor.fetchall()
            
            # Récupération des dénominations uniques
            query_denominations = f"""
                SELECT DISTINCT denomination
                FROM {universe}
                WHERE denomination IS NOT NULL AND denomination != ''
                ORDER BY denomination
            """
            
            cursor.execute(query_denominations)
            denominations = [row['denomination'] for row in cursor.fetchall()]
            
            # Préparation des données pour les tiroirs
            tiroirs = []
            
            # Configuration des tiroirs par univers
            if universe == 'mundo':
                # Configuration pour l'univers Mundo
                tiroirs = [
                    {'id': 'carre', 'titre': 'Carrés', 'icone': '◼', 'couleur': '#3498db'},
                    {'id': 'triangle', 'titre': 'Triangles', 'icone': '▲', 'couleur': '#2ecc71'},
                    {'id': 'cercle', 'titre': 'Cercles', 'icone': '●', 'couleur': '#f1c40f'},
                    {'id': 'rectangle', 'titre': 'Rectangles', 'icone': '▬', 'couleur': '#e74c3c'}
                ]
            elif universe == 'fruity':
                # Configuration pour l'univers Fruity
                tiroirs = [
                    {'id': 'fraise', 'titre': 'Fraises', 'icone': '🍓', 'couleur': '#e74c3c'},
                    {'id': 'citron', 'titre': 'Citrons', 'icone': '🍋', 'couleur': '#f1c40f'},
                    {'id': 'raisin', 'titre': 'Raisins', 'icone': '🍇', 'couleur': '#9b59b6'},
                    {'id': 'pasteque', 'titre': 'Pastèques', 'icone': '🍉', 'couleur': '#e74c3c'}
                ]
            elif universe == 'trigga':
                # Configuration pour l'univers Trigga
                tiroirs = [
                    {'id': 'trigga', 'titre': 'Trigga', 'icone': '▲', 'couleur': '#e67e22'},
                    {'id': 'flamme', 'titre': 'Flammes', 'icone': '🔥', 'couleur': '#e74c3c'},
                    {'id': 'eclair', 'titre': 'Éclairs', 'icone': '⚡', 'couleur': '#f1c40f'},
                    {'id': 'etoilefilante', 'titre': 'Étoiles filantes', 'icone': '☄', 'couleur': '#3498db'}
                ]
            elif universe == 'roaster':
                # Configuration pour l'univers Roaster
                tiroirs = [
                    {'id': 'roaster', 'titre': 'Roaster', 'icone': '☕', 'couleur': '#8e44ad'},
                    {'id': 'thermometre', 'titre': 'Thermomètres', 'icone': '🌡', 'couleur': '#e74c3c'},
                    {'id': 'soleil', 'titre': 'Soleils', 'icone': '☀', 'couleur': '#f1c40f'},
                    {'id': 'lune', 'titre': 'Lunes', 'icone': '🌙', 'couleur': '#3498db'}
                ]
            elif universe == 'sunshine':
                # Configuration pour l'univers Sunshine
                tiroirs = [
                    {'id': 'sunshine', 'titre': 'Sunshine', 'icone': '☀', 'couleur': '#f1c40f'},
                    {'id': 'nuage', 'titre': 'Nuages', 'icone': '☁', 'couleur': '#95a5a6'},
                    {'id': 'pluie', 'titre': 'Pluies', 'icone': '🌧', 'couleur': '#3498db'},
                    {'id': 'arcenciel', 'titre': 'Arcs-en-ciel', 'icone': '🌈', 'couleur': '#e74c3c'}
                ]
            else:
                # Configuration par défaut pour les autres univers
                tiroirs = [
                    {'id': 'forme1', 'titre': 'Forme 1', 'icone': '◼', 'couleur': '#3498db'},
                    {'id': 'forme2', 'titre': 'Forme 2', 'icone': '▲', 'couleur': '#2ecc71'},
                    {'id': 'forme3', 'titre': 'Forme 3', 'icone': '●', 'couleur': '#f1c40f'},
                    {'id': 'forme4', 'titre': 'Forme 4', 'icone': '▬', 'couleur': '#e74c3c'}
                ]
            
            # Création de la réponse
            reponse = {
                'univers': universe,
                'tiroirs': tiroirs,
                'total_formes': len(formes),
                'total_denominations': len(denominations),
                'formes': [
                    {
                        'nom': f['forme'],
                        'frequence': f['frequence'],
                        'type': f['type'],
                        'icone': get_forme_icon(f['forme']),
                        'couleur': get_forme_color(f['forme'])
                    }
                    for f in formes
                ],
                'denominations': denominations
            }
            
            return ReponseAPI.succes(donnees=reponse)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données des tiroirs: {str(e)}"
        )

@router.get("/universes/{universe}/legend-data", response_model=ReponseAPI)
async def get_legend_data(universe: str):
    """
    Récupère les données nécessaires pour l'affichage de la légende dans l'interface utilisateur.
    """
    try:
        # Validation de l'univers
        universe = validate_universe(universe)
        
        with get_db_cursor() as cursor:
            # Récupération des formes avec leurs fréquences et dénominations
            query = f"""
                SELECT 
                    f.forme,
                    f.frequence,
                    f.type,
                    d.denominations
                FROM (
                    SELECT 
                        forme,
                        COUNT(*) as frequence,
                        CASE WHEN forme LIKE '%-%' THEN 'composite' ELSE 'simple' END as type
                    FROM {universe}
                    WHERE forme IS NOT NULL AND forme != ''
                    GROUP BY forme
                ) f
                LEFT JOIN LATERAL (
                    SELECT jsonb_agg(DISTINCT denomination) as denominations
                    FROM {universe}
                    WHERE forme = f.forme 
                    AND denomination IS NOT NULL 
                    AND denomination != ''
                ) d ON true
                ORDER BY f.frequence DESC
            """
            
            cursor.execute(query)
            resultats = cursor.fetchall()
            
            # Traitement des résultats
            legend_items = []
            
            for row in resultats:
                forme_nom = row['forme']
                
                legend_items.append({
                    'forme': forme_nom,
                    'frequence': row['frequence'],
                    'type': row['type'],
                    'denominations': row['denominations'] or [],
                    'icone': get_forme_icon(forme_nom),
                    'couleur': get_forme_color(forme_nom)
                })
            
            # Création de la réponse
            reponse = {
                'univers': universe,
                'total_items': len(legend_items),
                'items': legend_items
            }
            
            return ReponseAPI.succes(donnees=reponse)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données de légende: {str(e)}"
        )
