from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from ..config import settings

class FormeType(str, Enum):
    SIMPLE = "simple"
    COMPOSITE = "composite"

class FormeBase(BaseModel):
    """Modèle de base pour une forme."""
    nom: str = Field(..., description="Nom de la forme (ex: 'carre', 'triangle')")
    type: FormeType = Field(..., description="Type de la forme (simple ou composite)")
    icone: Optional[str] = Field(None, description="Icône Unicode pour la forme")
    couleur: Optional[str] = Field(None, description="Couleur CSS pour la forme")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "nom": "carre",
                "type": "simple",
                "icone": "◼",
                "couleur": "#3498db"
            }
        }

class FormeAvecFrequence(FormeBase):
    """Modèle étendu pour une forme avec sa fréquence d'apparition."""
    frequence: int = Field(..., ge=0, description="Nombre d'occurrences de la forme")

class UniversFormes(BaseModel):
    """Modèle pour les formes disponibles dans un univers."""
    univers: str = Field(..., description="Nom de l'univers")
    formes: List[FormeAvecFrequence] = Field(..., description="Liste des formes avec leurs fréquences")
    total_formes: int = Field(..., description="Nombre total de formes uniques")
    formes_simples: List[str] = Field(..., description="Liste des noms des formes simples")
    formes_composites: List[str] = Field(..., description="Liste des noms des formes composites")

class ChipForme(BaseModel):
    """Modèle pour une forme associée à un chip."""
    forme: str = Field(..., description="Nom de la forme")
    denomination: str = Field(..., description="Dénomination de la forme")
    frequence: int = Field(1, description="Fréquence d'apparition de la forme sur le chip")

class ChipDetails(BaseModel):
    """Modèle pour les détails d'un chip."""
    chip_number: int = Field(..., description="Numéro du chip (1-48)")
    formes: List[ChipForme] = Field(..., description="Liste des formes du chip")
    univers: str = Field(..., description="Univers du chip")
    
    @validator('chip_number')
    def validate_chip_number(cls, v):
        if not 1 <= v <= 48:
            raise ValueError("Le numéro de chip doit être compris entre 1 et 48")
        return v

class UniversChips(BaseModel):
    """Modèle pour les chips d'un univers."""
    univers: str = Field(..., description="Nom de l'univers")
    chips: Dict[int, ChipDetails] = Field(..., description="Dictionnaire des chips par numéro")

class UniversMetadata(BaseModel):
    """Métadonnées d'un univers."""
    nom: str = Field(..., description="Nom de l'univers")
    description: Optional[str] = Field(None, description="Description de l'univers")
    couleurs: Dict[str, str] = Field(
        default_factory=lambda: {
            "primaire": "#2c3e50",
            "secondaire": "#34495e",
            "accent": "#3498db"
        },
        description="Schéma de couleurs de l'univers"
    )
    actif: bool = Field(True, description="Indique si l'univers est actif")
    
    @validator('nom')
    def validate_univers_name(cls, v):
        if v not in settings.VALID_UNIVERSES:
            raise ValueError(f"Univers non valide. Doit être l'un des suivants: {', '.join(settings.VALID_UNIVERSES)}")
        return v

class ReponseAPI(BaseModel):
    """Modèle de base pour les réponses de l'API."""
    succes: bool = Field(..., description="Indique si la requête a réussi")
    message: Optional[str] = Field(None, description="Message descriptif")
    donnees: Optional[Any] = Field(None, description="Données de la réponse")
    
    @classmethod
    def succes(cls, donnees: Any = None, message: str = "Opération réussie") -> 'ReponseAPI':
        return cls(succes=True, message=message, donnees=donnees)
    
    @classmethod
    def erreur(cls, message: str = "Une erreur est survenue", donnees: Any = None) -> 'ReponseAPI':
        return cls(succes=False, message=message, donnees=donnees)
