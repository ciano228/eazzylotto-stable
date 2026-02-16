"""
Advanced Statistics Service
Calculates normalized overdue scores for attributes with dynamic cardinality support
"""

from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.connection import get_db
from app.models.combination import Combination
from app.services.analysis_service import AnalysisService


# Cardinalités fixes (ne varient jamais)
FIXED_CARDINALITIES = {
    'chip': 48,
    'tome': 4,
    'granque': 6,
    'ligne': 8,
    'colonne': 6,
    'petique': 4,
    'parite': 4
}

# Cardinalités dynamiques selon l'univers
FORME_CARDINALITY = {
    'mundo': 4,
    'fruity': 4,
    'trigga': 10,
    'roaster': 12,
    'sunshine': 16
}

# Seuil pour déclarer un attribut "vraiment du"
OVERDUE_THRESHOLD = 2.5


class AdvancedStatisticsService:
    
    @staticmethod
    def get_attribute_cardinality(
        attr_type: str,
        universe: str,
        session_data: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> int:
        """
        Retourne la cardinalité d'un type d'attribut selon le contexte
        
        Args:
            attr_type: Type d'attribut ('chip', 'tome', 'forme', 'denomination', etc.)
            universe: Univers sélectionné
            session_data: Données de session (optionnel)
            db: Session de base de données (pour cardinalités contextuelles)
        """
        # Cardinalités fixes
        if attr_type in FIXED_CARDINALITIES:
            return FIXED_CARDINALITIES[attr_type]
        
        # Cardinalités dynamiques selon l'univers
        if attr_type == 'forme':
            return FORME_CARDINALITY.get(universe.lower(), 4)
        
        # Cardinalités contextuelles (requête DB)
        if attr_type == 'denomination':
            if db is None:
                db = next(get_db())
            count = db.execute(
                select(func.count(func.distinct(Combination.denomination)))
                .where(Combination.universe == universe)
            ).scalar()
            return count or 1
        
        if attr_type == 'combination':
            if db is None:
                db = next(get_db())
            count = db.execute(
                select(func.count(Combination.id))
                .where(Combination.universe == universe)
            ).scalar()
            return count or 1
        
        # Fallback: retourner 48 par défaut
        return 48
    
    @staticmethod
    def get_chips_for_filter(
        filter_type: str,
        filter_value: Any,
        universe: str,
        session_data: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Set[int]:
        """
        Retourne l'ensemble des chips satisfaisant un filtre spécifique
        
        Args:
            filter_type: Type de filtre ('tome', 'forme', 'ligne', etc.)
            filter_value: Valeur du filtre
            universe: Univers sélectionné
            session_data: Données de session
            db: Session DB
        """
        # Filtre par tome (12 chips par tome)
        if filter_type == 'tome':
            tome_num = int(str(filter_value).replace('tome', ''))
            start = (tome_num - 1) * 12 + 1
            end = tome_num * 12
            return set(range(start, end + 1))
        
        # Filtre par granque (8 chips par granque)
        if filter_type == 'granque':
            granque_num = int(str(filter_value).replace('Q', '').replace('q', ''))
            start = (granque_num - 1) * 8 + 1
            end = granque_num * 8
            return set(range(start, end + 1))
        
        # Filtre par ligne (6 chips par ligne)
        if filter_type == 'ligne':
            ligne_num = int(filter_value)
            return set(range(ligne_num, 49, 8))
        
        # Filtre par colonne (8 chips par colonne)
        if filter_type == 'colonne':
            col_num = int(filter_value)
            chips = []
            for row in range(8):
                chip = row * 6 + col_num
                if 1 <= chip <= 48:
                    chips.append(chip)
            return set(chips)
        
        # Filtre par petique (12 chips par petique)
        if filter_type == 'petique':
            petique_map = {
                'q1': set(range(1, 13)),
                'q2': set(range(13, 25)),
                'q3': set(range(25, 37)),
                'q4': set(range(37, 49))
            }
            return petique_map.get(str(filter_value).lower(), set())
        
        # Filtre par forme (requête DB)
        if filter_type == 'forme':
            if db is None:
                db = next(get_db())
            forme_value = str(filter_value).lower()
            combinations = db.execute(
                select(Combination.chip_numbers)
                .where(Combination.universe == universe)
                .where(func.lower(Combination.forme).like(f'%{forme_value}%'))
            ).scalars().all()
            
            chips = set()
            for combo_chips in combinations:
                if combo_chips:
                    chips.update(combo_chips)
            return chips
        
        # Filtre par parité
        if filter_type == 'parite':
            if filter_value == 'pair':
                return set(range(2, 49, 2))
            elif filter_value == 'impair':
                return set(range(1, 49, 2))
        
        # Pas de filtre reconnu: retourner tous les chips
        return set(range(1, 49))
    
    @staticmethod
    def calculate_filtered_cardinality(
        filters: Dict[str, Any],
        universe: str,
        session_data: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calcule la cardinalité d'un ensemble filtré (intersection de tous les filtres)
        
        Args:
            filters: Dictionnaire {filter_type: filter_value}
            universe: Univers sélectionné
            session_data: Données de session
            db: Session DB
        
        Returns:
            {
                'total_cardinality': int,
                'valid_chips': Set[int],
                'description': str
            }
        """
        # Commencer avec l'ensemble complet
        valid_chips = set(range(1, 49))
        filter_descriptions = []
        
        # Appliquer chaque filtre (intersection)
        for filter_type, filter_value in filters.items():
            if not filter_value:
                continue
            
            filter_chips = AdvancedStatisticsService.get_chips_for_filter(
                filter_type, filter_value, universe, session_data, db
            )
            valid_chips &= filter_chips
            filter_descriptions.append(f"{filter_type}({filter_value})")
        
        # Description lisible
        description = " ∩ ".join(filter_descriptions) if filter_descriptions else "Tous les éléments"
        
        return {
            'total_cardinality': len(valid_chips),
            'valid_chips': valid_chips,
            'description': description,
            'filters_applied': filters
        }
    
    @staticmethod
    def calculate_overdue_score(
        attr_type: str,
        attr_value: Any,
        gap: int,
        total_draws: int,
        universe: str,
        filters: Optional[Dict] = None,
        session_data: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calcule le score de surécart normalisé pour un attribut
        
        Returns:
            {
                'score': float,
                'is_overdue': bool,
                'expected_gap': float,
                'cardinality': int,
                'gap': int
            }
        """
        # Obtenir la cardinalité
        if filters:
            filtered_result = AdvancedStatisticsService.calculate_filtered_cardinality(
                filters, universe, session_data, db
            )
            cardinality = filtered_result['total_cardinality']
        else:
            cardinality = AdvancedStatisticsService.get_attribute_cardinality(
                attr_type, universe, session_data, db
            )
        
        # Éviter division par zéro
        if cardinality == 0 or total_draws == 0:
            return {
                'score': 0,
                'is_overdue': False,
                'expected_gap': 0,
                'cardinality': cardinality,
                'gap': gap
            }
        
        # Calculer l'écart attendu
        expected_gap = total_draws * (1 / cardinality)
        
        # Score de surécart
        if expected_gap > 0:
            score = gap / expected_gap
        else:
            score = 0
        
        # Déterminer si vraiment du
        is_overdue = score > OVERDUE_THRESHOLD
        
        return {
            'score': round(score, 2),
            'is_overdue': is_overdue,
            'expected_gap': round(expected_gap, 2),
            'cardinality': cardinality,
            'gap': gap
        }
    
    @staticmethod
    def calculate_session_overdue_stats(
        session_id: int,
        universe: str,
        filters: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calcule toutes les statistiques d'écart pour une session
        
        Returns:
            {
                'filtered_set': {...},
                'attributes': [...]
            }
        """
        if db is None:
            db = next(get_db())
        
        # Récupérer les données de la session via AnalysisService
        journal_data = AnalysisService.generate_statistical_journal(db=db, session_id=session_id, universe=universe)
        
        if not journal_data or ('journal' not in journal_data and 'draws' not in journal_data):
            return {
                'filtered_set': {'description': 'Aucune donnée', 'total_cardinality': 0},
                'attributes': [],
                'total_draws': 0
            }
        
        entries = journal_data.get('journal', [])
        total_draws = len(set(e.get('draw_id') for e in entries if e.get('status') == 'completed'))
        
        if total_draws == 0:
            return {
                'filtered_set': {'description': 'Aucun tirage valide', 'total_cardinality': 0},
                'attributes': [],
                'total_draws': 0
            }
        
        # Info sur l'ensemble filtré
        if filters:
            filtered_info = AdvancedStatisticsService.calculate_filtered_cardinality(
                filters, universe, None, db
            )
        else:
            filtered_info = {
                'description': 'Tous les éléments',
                'total_cardinality': 48,
                'valid_chips': set(range(1, 49))
            }
        
        # Calculer les gaps pour tous les attributs depuis les draws
        attributes_stats = []
        
        # Calcul pour TOUS les chips (1-48)
        chip_last_seen = {}
        # grouper les entrées par tirage pour compter un tirage comme 1 unité de gap
        draw_entries = defaultdict(list)
        for e in entries:
            draw_entries[e.get('draw_id')].append(e)
            
        # Trier les tirages par date/id si possible, mais on va juste itérer sur les entrées complétées
        # On a besoin de l'ordre chronologique. Les entries sont déjà triées par AnalysisService.
        
        # On va plutôt itérer sur les entries directement mais garder trace du dernier draw_id vu
        current_draw_index = 0
        last_draw_id = None
        
        for e in entries:
            if e.get('status') != 'completed':
                continue
            
            if e.get('draw_id') != last_draw_id:
                current_draw_index += 1
                last_draw_id = e.get('draw_id')
            
            # Traiter les attributs de cette entrée de combinaison
            # Chips
            c_val = e.get('chip')
            if c_val:
                try:
                    # Robust parsing for 'chip1', 'Chip 1', '1', etc.
                    s_val = str(c_val).lower().strip().replace('chip', '').replace(' ', '')
                    c_num = int(s_val)
                    chip_last_seen[c_num] = current_draw_index
                except Exception as ex:
                    print(f"DEBUG: Failed to parse chip value '{c_val}': {ex}")
                    pass
            
            # Autres attributs
            for attr_type in FIXED_CARDINALITIES.keys():
                if attr_type == 'chip': continue
                
                val = e.get(attr_type)
                if val and val != "---":
                    # Trouver l'attribut dans attributes_stats ou le créer
                    found = False
                    for a_s in attributes_stats:
                        if a_s['type'] == attr_type and a_s['value'] == val:
                            a_s['last_seen_index'] = current_draw_index
                            found = True
                            break
                    if not found:
                        attributes_stats.append({
                            'type': attr_type,
                            'value': val,
                            'last_seen_index': current_draw_index
                        })
        
        # Mettre à jour total_draws réelement vus
        total_draws = current_draw_index
        
        # Finaliser le calcul des scores pour TOUS les attributs trouvés
        final_stats = []
        
        # 1. Traiter les Chips
        for c_num in range(1, 49):
            if c_num not in filtered_info.get('valid_chips', set(range(1, 49))):
                continue
                
            last_idx = chip_last_seen.get(c_num, 0)
            gap = total_draws - last_idx
            cardinality = 48
            expected_gap = total_draws * (1.0 / cardinality)
            score = gap / expected_gap if expected_gap > 0 else 0
            
            final_stats.append({
                'type': 'chip',
                'value': f"chip{c_num}",
                'gap': gap,
                'expected_gap': round(expected_gap, 2),
                'score': round(score, 2),
                'cardinality': cardinality
            })
            
        # 2. Ajouter les autres attributs collectés
        # attributes_stats contient déjà type, value, last_seen_index
        for a_s in attributes_stats:
            attr_type = a_s['type']
            if attr_type == 'chip': continue # Déjà fait
            
            card = FIXED_CARDINALITIES.get(attr_type, 1)
            last_idx = a_s['last_seen_index']
            gap = total_draws - last_idx
            
            expected_gap = total_draws * (1.0 / card)
            score = gap / expected_gap if expected_gap > 0 else 0
            
            final_stats.append({
                'type': attr_type,
                'value': a_s['value'],
                'gap': gap,
                'expected_gap': round(expected_gap, 2),
                'score': round(score, 2),
                'cardinality': card
            })
            
        return {
            'total_draws': total_draws,
            'filtered_set': {
                'description': filtered_info['description'],
                'total_cardinality': filtered_info['total_cardinality']
            },
            'attributes': sorted(final_stats, key=lambda x: x['score'], reverse=True)
        }
