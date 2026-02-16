"""
Service de Gestion des Poids Structurels Katula
Calcule et fournit les cardinalités, probabilités et gaps attendus
pour chaque élément (chip, ligne, colonne, etc.) dans chaque univers
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.combination import Combination


class StructuralWeightService:
    """Service pour gérer les poids structurels des éléments Katula"""
    
    # Cardinalités totales par univers (pré-calculées)
    UNIVERSE_TOTALS = {
        'mundo': 544,
        'fruity': 435,
        'trigga': 300,
        'roaster': 171,
        'sunshine': 153
    }
    
    @staticmethod
    def get_total_combinations(universe: str) -> int:
        """Récupère le nombre total de combinaisons pour un univers"""
        return StructuralWeightService.UNIVERSE_TOTALS.get(universe.lower(), 544)
    
    @staticmethod
    def calculate_cardinality(
        db: Session,
        universe: str,
        attribute_type: str,
        attribute_value: str
    ) -> int:
        """
        Calcule la cardinalité (nombre de combinaisons) pour un élément spécifique
        
        Args:
            db: Session de base de données
            universe: Univers (mundo, fruity, etc.)
            attribute_type: Type d'attribut (chip, ligne, colonne, forme, etc.)
            attribute_value: Valeur de l'attribut (chip_5, ligne1, carre, etc.)
        
        Returns:
            Nombre de combinaisons contenant cet élément
        """
        query = db.query(func.count(Combination.combination_id)).filter(
            Combination.univers == universe
        )
        
        # Filtrer selon le type d'attribut
        if attribute_type == 'chip':
            query = query.filter(Combination.chip == attribute_value)
        elif attribute_type == 'ligne':
            query = query.filter(Combination.ligne == attribute_value)
        elif attribute_type == 'colonne':
            query = query.filter(Combination.colonne == attribute_value)
        elif attribute_type == 'forme':
            query = query.filter(Combination.forme == attribute_value)
        elif attribute_type == 'engine':
            query = query.filter(Combination.engine == attribute_value)
        elif attribute_type == 'beastie':
            query = query.filter(Combination.beastie == attribute_value)
        elif attribute_type == 'tome':
            query = query.filter(Combination.tome == attribute_value)
        elif attribute_type == 'denomination':
            query = query.filter(Combination.denomination == attribute_value)
        elif attribute_type == 'alpha_ranking':
            query = query.filter(Combination.alpha_ranking == attribute_value)
        elif attribute_type == 'granque':
            query = query.filter(Combination.granque_name == attribute_value)
        elif attribute_type == 'petique':
            query = query.filter(Combination.petique == attribute_value)
        elif attribute_type == 'parite':
            # Nécessite une jointure ou un champ direct
            pass
        elif attribute_type == 'unidos':
            # Nécessite une jointure ou un champ direct
            pass
        
        return query.scalar() or 0
    
    @staticmethod
    def calculate_probability(cardinality: int, total_universe: int) -> float:
        """
        Calcule la probabilité structurelle d'apparition
        
        Args:
            cardinality: Nombre de combinaisons de l'élément
            total_universe: Nombre total de combinaisons dans l'univers
        
        Returns:
            Probabilité (0.0 à 1.0)
        """
        if total_universe == 0:
            return 0.0
        return cardinality / total_universe
    
    @staticmethod
    def calculate_expected_gap(probability: float) -> float:
        """
        Calcule le gap attendu (nombre moyen de tirages entre deux apparitions)
        
        Args:
            probability: Probabilité d'apparition par tirage
        
        Returns:
            Gap attendu en nombre de tirages
        """
        if probability == 0:
            return float('inf')
        return 1.0 / probability
    
    @staticmethod
    def get_structural_weight(
        db: Session,
        universe: str,
        attribute_type: str,
        attribute_value: str
    ) -> Dict[str, Any]:
        """
        Récupère le poids structurel complet pour un élément
        
        Returns:
            Dict contenant:
            - cardinality: Nombre de combinaisons
            - total_universe: Total combinaisons univers
            - probability: Probabilité d'apparition
            - expected_gap: Gap attendu
            - weight: Poids normalisé (= probability)
        """
        total = StructuralWeightService.get_total_combinations(universe)
        cardinality = StructuralWeightService.calculate_cardinality(
            db, universe, attribute_type, attribute_value
        )
        probability = StructuralWeightService.calculate_probability(cardinality, total)
        expected_gap = StructuralWeightService.calculate_expected_gap(probability)
        
        return {
            'universe': universe,
            'attribute_type': attribute_type,
            'attribute_value': attribute_value,
            'cardinality': cardinality,
            'total_universe': total,
            'probability': round(probability, 6),
            'expected_gap': round(expected_gap, 2),
            'weight': round(probability, 6)
        }
    
    @staticmethod
    def get_all_weights_for_attribute(
        db: Session,
        universe: str,
        attribute_type: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Récupère les poids structurels pour toutes les valeurs d'un attribut
        
        Returns:
            Dict {attribute_value: weight_info}
        """
        # Récupérer toutes les valeurs distinctes pour cet attribut
        query = db.query(Combination).filter(Combination.univers == universe)
        
        if attribute_type == 'chip':
            values = db.query(Combination.chip).filter(
                Combination.univers == universe
            ).distinct().all()
            values = [v[0] for v in values if v[0]]
        elif attribute_type == 'ligne':
            values = db.query(Combination.ligne).filter(
                Combination.univers == universe
            ).distinct().all()
            values = [v[0] for v in values if v[0]]
        elif attribute_type == 'forme':
            values = db.query(Combination.forme).filter(
                Combination.univers == universe
            ).distinct().all()
            values = [v[0] for v in values if v[0]]
        else:
            values = []
        
        weights = {}
        for value in values:
            weights[value] = StructuralWeightService.get_structural_weight(
                db, universe, attribute_type, value
            )
        
        return weights
    
    @staticmethod
    def calculate_gap_score(
        current_gap: int,
        universe: str,
        attribute_type: str,
        attribute_value: str,
        db: Session
    ) -> float:
        """
        Calcule le score de gap normalisé par le poids structurel
        
        Args:
            current_gap: Gap actuel observé
            universe: Univers
            attribute_type: Type d'attribut
            attribute_value: Valeur de l'attribut
            db: Session de base de données
        
        Returns:
            Score normalisé (< 1 = chaud, = 1 = normal, > 1 = froid)
        """
        weight = StructuralWeightService.get_structural_weight(
            db, universe, attribute_type, attribute_value
        )
        expected_gap = weight['expected_gap']
        
        if expected_gap == 0 or expected_gap == float('inf'):
            return 0.0
        
        return current_gap / expected_gap
    
    @staticmethod
    def predict_appearance_probability(
        current_gap: int,
        n_draws: int,
        universe: str,
        attribute_type: str,
        attribute_value: str,
        db: Session
    ) -> float:
        """
        Prédit la probabilité d'apparition dans les N prochains tirages
        
        Args:
            current_gap: Gap actuel
            n_draws: Nombre de tirages futurs à considérer
            universe: Univers
            attribute_type: Type d'attribut
            attribute_value: Valeur de l'attribut
            db: Session de base de données
        
        Returns:
            Probabilité (0.0 à 1.0)
        """
        weight = StructuralWeightService.get_structural_weight(
            db, universe, attribute_type, attribute_value
        )
        prob_per_draw = weight['probability']
        
        # Probabilité de NE PAS apparaître dans N tirages
        prob_not_appear = (1 - prob_per_draw) ** n_draws
        
        # Probabilité d'apparaître au moins une fois
        prob_appear = 1 - prob_not_appear
        
        return round(prob_appear, 4)
    
    @staticmethod
    def get_universe_statistics(db: Session, universe: str) -> Dict[str, Any]:
        """
        Récupère les statistiques globales d'un univers
        
        Returns:
            Dict avec statistiques par type d'attribut
        """
        total = StructuralWeightService.get_total_combinations(universe)
        
        stats = {
            'universe': universe,
            'total_combinations': total,
            'attributes': {}
        }
        
        # Pour chaque type d'attribut, calculer les statistiques
        for attr_type in ['chip', 'ligne', 'colonne', 'forme']:
            weights = StructuralWeightService.get_all_weights_for_attribute(
                db, universe, attr_type
            )
            
            stats['attributes'][attr_type] = {
                'count': len(weights),
                'values': weights
            }
        
        return stats
