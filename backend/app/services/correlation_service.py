
from typing import Dict, List, Any, Tuple
import logging
from collections import defaultdict
import itertools
from sqlalchemy.orm import Session
from sqlalchemy import text
from session_statistics_engine import SessionStatisticsEngine

logger = logging.getLogger(__name__)

class CorrelationService:
    """
    Service pour analyser les corrélations entre attributs (Co-occurence, Confiance, Support).
    Répond à la question: "Quel attribut implique quel autre?"
    """

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        # Réutilise l'engine pour charger le mapping et logique de parsing
        self.stats_engine = SessionStatisticsEngine(db_config)
        self.universe_map = None

    def analyze_correlations(self, session_draws: List[Dict[str, Any]], universe: str = 'mundo') -> Dict[str, Any]:
        """
        Calcule la matrice de corrélation pour les attributs donnés.
        """
        if not session_draws:
            return {}

        # 1. Charger Mapping (si pas déjà fait pour cet univers)
        # Note: L'engine a sa propre méthode de cache interne si on l'instanciait une seule fois, 
        # mais ici on le fait à la demande.
        self.universe_map = self.stats_engine._load_universe_map(universe)
        if not self.universe_map:
            return {"error": f"No mapping for universe {universe}"}

        # 2. Extract Attributes per Draw
        # draw_attributes: List[List[str]] -> Chaque élément est une liste de "Key:Value" pour un tirage
        # ex: ["forme:Triangle", "engine:Ambulance", ...]
        draw_transactions = []

        for draw in session_draws:
            winning_numbers = draw.get('winning_numbers', [])
            valid_numbers = [int(n) for n in winning_numbers if str(n).isdigit()]
            
            if len(valid_numbers) < 2:
                continue

            # Generate Pairs
            pairs = list(itertools.combinations(valid_numbers, 2))
            
            # Collect UNIQUE attributes for this entire draw (across all pairs)
            # Or should it be per pair? The user asks "what implies what".
            # Usually we want "In a draw, if Triangle appears, does Ambulance appear?"
            # So we treat the DRAW as the transaction.
            
            draw_attrs_set = set()
            
            for p in pairs:
                p_key = tuple(sorted(p))
                if p_key in self.universe_map:
                    attrs_list = self.universe_map[p_key]
                    for attrs in attrs_list:
                         for key, val in attrs.items():
                             if key in ['value', 'ligne', 'colonne', 'dates', 'last_draw_index', 'last_draw_date']:
                                 continue
                             if val and val != "---":
                                 # Format: "Type:Value"
                                 normalized_key = key.replace('_name', '')
                                 if key == 'base_name': normalized_key = 'base_name'
                                 
                                 item_str = f"{normalized_key}:{val}"
                                 draw_attrs_set.add(item_str)
            
            if draw_attrs_set:
                draw_transactions.append(list(draw_attrs_set))

        # 3. Calculate Co-occurrences
        # Count(A), Count(A & B)
        item_counts = defaultdict(int)
        pair_counts = defaultdict(int)
        total_transactions = len(draw_transactions)

        for transaction in draw_transactions:
            # Count individuals
            for item in transaction:
                item_counts[item] += 1
            
            # Count pairs involved in this transaction
            # We generate pairs of attributes present in the draw
            # e.g. (forme:Triangle, engine:Ambulance)
            for item_a, item_b in itertools.combinations(sorted(transaction), 2):
                pair_counts[(item_a, item_b)] += 1

        # 4. Build Rules / Heatmap Data
        # We want to return a list of correlations
        correlations = []
        
        # Thresholds (can be params later)
        min_support = 0.05 # 5% of draws
        min_confidence = 0.50 # 50% implication

        for (item_a, item_b), pair_count in pair_counts.items():
            # Support = P(A & B)
            support = pair_count / total_transactions
            
            if support < min_support:
                continue

            # Direction 1: A -> B
            # Confidence = P(B|A) = Count(A&B) / Count(A)
            count_a = item_counts[item_a]
            conf_a_to_b = pair_count / count_a if count_a > 0 else 0
            
            # Direction 2: B -> A
            count_b = item_counts[item_b]
            conf_b_to_a = pair_count / count_b if count_b > 0 else 0
            
            # Add significant rules
            if conf_a_to_b >= min_confidence:
                correlations.append({
                    "antecedent": item_a,
                    "consequent": item_b,
                    "confidence": round(conf_a_to_b, 2),
                    "support": round(support, 2),
                    "count": pair_count,
                    "rule": f"If {item_a} then {item_b}"
                })
            
            if conf_b_to_a >= min_confidence:
                correlations.append({
                    "antecedent": item_b,
                    "consequent": item_a,
                    "confidence": round(conf_b_to_a, 2),
                    "support": round(support, 2),
                    "count": pair_count,
                    "rule": f"If {item_b} then {item_a}"
                })

        # Sort by Confidence desc
        correlations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "total_draws_analyzed": total_transactions,
            "rule_count": len(correlations),
            "top_correlations": correlations[:100] # Limit size
        }
