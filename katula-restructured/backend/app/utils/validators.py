"""
Module de validation des données pour l'API Katula.
"""
from typing import Any, Optional
from fastapi import HTTPException, status
from ..config import settings
import re

def validate_universe(universe: str) -> str:
    """
    Valide qu'un nom d'univers est valide.
    
    Args:
        universe: Le nom de l'univers à valider
        
    Returns:
        str: Le nom de l'univers en minuscules si valide
        
    Raises:
        HTTPException: Si l'univers n'est pas valide
    """
    if not universe or not isinstance(universe, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'universe' est requis et doit être une chaîne de caractères."
        )
    
    universe = universe.lower()
    if universe not in settings.VALID_UNIVERSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Univers non valide. Les univers valides sont: {', '.join(settings.VALID_UNIVERSES)}"
        )
    
    return universe

def validate_chip_number(chip_number: int) -> int:
    """
    Valide qu'un numéro de chip est valide (entre 1 et 48).
    
    Args:
        chip_number: Le numéro de chip à valider
        
    Returns:
        int: Le numéro de chip si valide
        
    Raises:
        HTTPException: Si le numéro de chip n'est pas valide
    """
    if not isinstance(chip_number, int) or not (1 <= chip_number <= 48):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le numéro de chip doit être un entier entre 1 et 48"
        )
    return chip_number

def validate_forme(forme: str) -> str:
    """
    Valide le format d'un nom de forme.
    
    Args:
        forme: Le nom de la forme à valider
        
    Returns:
        str: Le nom de la forme en minuscules si valide
        
    Raises:
        HTTPException: Si le format du nom de forme n'est pas valide
    """
    if not forme or not isinstance(forme, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom de la forme est requis et doit être une chaîne de caractères."
        )
    
    forme = forme.strip().lower()
    if not re.match(r'^[a-z0-9-]+$', forme):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom de la forme ne doit contenir que des lettres minuscules, des chiffres et des tirets."
        )
    
    return forme

def validate_limit_offset(limit: int = 100, offset: int = 0) -> tuple[int, int]:
    """
    Valide et normalise les paramètres de pagination.
    
    Args:
        limit: Nombre maximum d'éléments à retourner (1-1000)
        offset: Nombre d'éléments à sauter
        
    Returns:
        tuple: (limit, offset) validés
    """
    try:
        limit = max(1, min(int(limit), 1000))  # Limite entre 1 et 1000
        offset = max(0, int(offset))  # Offset minimum de 0
        return limit, offset
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les paramètres 'limit' et 'offset' doivent être des nombres entiers valides."
        )

def validate_json_payload(payload: dict, required_fields: list[str]) -> None:
    """
    Valide qu'un payload JSON contient tous les champs requis.
    
    Args:
        payload: Le dictionnaire à valider
        required_fields: Liste des clés requises
        
    Raises:
        HTTPException: Si un champ requis est manquant
    """
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le corps de la requête doit être un objet JSON valide."
        )
    
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Champs obligatoires manquants: {', '.join(missing_fields)}"
        )

def get_forme_icon(forme: str) -> str:
    """
    Retourne l'icône correspondant à une forme.
    
    Args:
        forme: Le nom de la forme
        
    Returns:
        str: Le caractère Unicode de l'icône
    """
    icons = {
        'carre': '◼',
        'triangle': '▲',
        'cercle': '●',
        'rectangle': '▬',
        'etoile': '★',
        'losange': '◆',
        'croix': '✚',
        'coeur': '❤',
        'trigga': '▲',
        'flamme': '🔥',
        'eclair': '⚡',
        'etoilefilante': '☄',
        'roaster': '☕',
        'thermometre': '🌡',
        'soleil': '☀',
        'lune': '🌙',
        'sunshine': '☀',
        'nuage': '☁',
        'pluie': '🌧',
        'arcenciel': '🌈',
    }
    return icons.get(forme.lower(), '❓')

def get_forme_color(forme: str) -> str:
    """
    Retourne la couleur CSS correspondant à une forme.
    
    Args:
        forme: Le nom de la forme
        
    Returns:
        str: Le code couleur CSS
    """
    colors = {
        'carre': '#3498db',    # Bleu
        'triangle': '#2ecc71', # Vert
        'cercle': '#f1c40f',  # Jaune
        'rectangle': '#e74c3c',# Rouge
        'etoile': '#f39c12',  # Orange
        'losange': '#9b59b6', # Violet
        'croix': '#34495e',   # Gris foncé
        'coeur': '#e74c3c',   # Rouge
        'trigga': '#e67e22',  # Orange foncé
        'flamme': '#e74c3c',  # Rouge
        'eclair': '#f1c40f',  # Jaune
        'etoilefilante': '#3498db', # Bleu
        'roaster': '#8e44ad', # Violet foncé
        'thermometre': '#e74c3c',   # Rouge
        'soleil': '#f1c40f',  # Jaune
        'lune': '#3498db',    # Bleu
        'sunshine': '#f1c40f',# Jaune
        'nuage': '#95a5a6',   # Gris
        'pluie': '#3498db',   # Bleu
        'arcenciel': '#e74c3c', # Rouge (première couleur de l'arc-en-ciel)
    }
    return colors.get(forme.lower(), '#95a5a6')  # Gris par défaut
