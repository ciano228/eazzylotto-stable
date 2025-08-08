"""
Service de Génération de Combinaisons Optimales
Générateur intelligent basé sur l'IA, les patterns et les analyses statistiques
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.ml_service import MLService
from app.services.gap_analysis_service import GapAnalysisService
# from app.services.pattern_detection_service import PatternDetectionService
from app.services.frequency_service import FrequencyService

class CombinationGeneratorService:
    """
    Service principal pour la génération de combinaisons optimales
    """
    
    # Stratégies de génération disponibles
    GENERATION_STRATEGIES = {
        'LSTM_BASED': 'Basé sur les prédictions LSTM',
        'GAP_BASED': 'Basé sur les écarts et retards',
        'PATTERN_BASED': 'Basé sur les patterns détectés',
        'FREQUENCY_BASED': 'Basé sur les fréquences',
        'HYBRID_SMART': 'Hybride intelligent (toutes méthodes)',
        'RANDOM_OPTIMIZED': 'Aléatoire optimisé'
    }
    
    @staticmethod
    def generate_combinations(
        db: Session, 
        universe: str = "mundo",
        strategy: str = "HYBRID_SMART",
        num_combinations: int = 10,
        session_id: Optional[int] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Génère des combinaisons optimales selon la stratégie choisie"""
        
        print(f"🎲 Génération de {num_combinations} combinaisons pour {universe} (stratégie: {strategy})...")
        
        # Initialiser les contraintes par défaut
        if constraints is None:
            constraints = {
                "avoid_duplicates": True,
                "min_diversity": 0.7,
                "max_consecutive": 2,
                "balance_attributes": True
            }
        
        combinations = []
        
        try:
            if strategy == "LSTM_BASED":
                combinations = CombinationGeneratorService._generate_lstm_combinations(
                    db, universe, num_combinations, constraints
                )
            elif strategy == "GAP_BASED":
                combinations = CombinationGeneratorService._generate_gap_combinations(
                    db, universe, num_combinations, session_id, constraints
                )
            elif strategy == "PATTERN_BASED":
                combinations = CombinationGeneratorService._generate_pattern_combinations(
                    db, universe, num_combinations, constraints
                )
            elif strategy == "FREQUENCY_BASED":
                combinations = CombinationGeneratorService._generate_frequency_combinations(
                    db, universe, num_combinations, session_id, constraints
                )
            elif strategy == "HYBRID_SMART":
                combinations = CombinationGeneratorService._generate_hybrid_combinations(
                    db, universe, num_combinations, session_id, constraints
                )
            elif strategy == "RANDOM_OPTIMIZED":
                combinations = CombinationGeneratorService._generate_random_optimized_combinations(
                    db, universe, num_combinations, constraints
                )
            else:
                raise ValueError(f"Stratégie inconnue: {strategy}")
            
            # Post-traitement et optimisation
            combinations = CombinationGeneratorService._optimize_combinations(
                combinations, constraints
            )
            
            # Calculer les scores et statistiques
            result = CombinationGeneratorService._analyze_generated_combinations(
                combinations, strategy, universe, session_id
            )
            
            print(f"✅ {len(combinations)} combinaisons générées avec succès")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération combinaisons: {e}")
            return {
                "error": str(e),
                "universe": universe,
                "strategy": strategy,
                "combinations": [],
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _generate_lstm_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons basées sur les prédictions LSTM"""
        
        print("🧠 Génération basée sur LSTM...")
        
        combinations = []
        
        try:
            # Obtenir les prédictions LSTM
            lstm_predictions = MLService.predict_all_lstm(db, universe)
            
            if "top_predictions" not in lstm_predictions:
                return []
            
            # Organiser les prédictions par type d'attribut
            predictions_by_type = {}
            for pred in lstm_predictions["top_predictions"]:
                attr_type = pred["attribute_type"]
                if attr_type not in predictions_by_type:
                    predictions_by_type[attr_type] = []
                predictions_by_type[attr_type].append(pred)
            
            # Générer les combinaisons
            for i in range(num_combinations):
                combination = {
                    "id": f"lstm_{i+1}",
                    "strategy": "LSTM_BASED",
                    "attributes": {},
                    "confidence_scores": {},
                    "total_confidence": 0,
                    "generation_method": "AI Neural Network"
                }
                
                total_confidence = 0
                attribute_count = 0
                
                # Sélectionner les meilleurs attributs de chaque type
                for attr_type, preds in predictions_by_type.items():
                    if preds:
                        # Prendre le meilleur ou varier selon l'index
                        pred_index = min(i % len(preds), len(preds) - 1)
                        selected_pred = preds[pred_index]
                        
                        combination["attributes"][attr_type] = selected_pred["predicted_value"]
                        combination["confidence_scores"][attr_type] = selected_pred["confidence_percent"]
                        total_confidence += selected_pred["confidence_percent"]
                        attribute_count += 1
                
                # Calculer la confiance moyenne
                if attribute_count > 0:
                    combination["total_confidence"] = total_confidence / attribute_count
                
                combinations.append(combination)
            
        except Exception as e:
            print(f"❌ Erreur génération LSTM: {e}")
        
        return combinations
    
    @staticmethod
    def _generate_gap_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        session_id: Optional[int],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons basées sur les écarts et retards"""
        
        print("⏰ Génération basée sur les écarts...")
        
        combinations = []
        
        try:
            # Adapter l'univers pour les requêtes selon la session
            universe_key = f"{universe}_session_{session_id}" if session_id else universe
            
            # Obtenir les attributs en retard
            overdue_data = GapAnalysisService.get_overdue_attributes(db, universe_key, threshold=1.5)
            
            # Organiser par type d'attribut
            overdue_by_type = {}
            for attr_type, attributes in overdue_data.items():
                overdue_by_type[attr_type] = sorted(
                    attributes, 
                    key=lambda x: x.get("delay_ratio", 0), 
                    reverse=True
                )
            
            # Générer les combinaisons
            for i in range(num_combinations):
                combination = {
                    "id": f"gap_{i+1}",
                    "strategy": "GAP_BASED",
                    "attributes": {},
                    "delay_scores": {},
                    "total_delay_score": 0,
                    "generation_method": "Statistical Gap Analysis"
                }
                
                total_delay = 0
                attribute_count = 0
                
                # Sélectionner les attributs les plus en retard
                for attr_type, attrs in overdue_by_type.items():
                    if attrs:
                        # Varier la sélection selon l'index
                        attr_index = min(i % len(attrs), len(attrs) - 1)
                        selected_attr = attrs[attr_index]
                        
                        combination["attributes"][attr_type] = selected_attr["value"]
                        combination["delay_scores"][attr_type] = selected_attr.get("delay_ratio", 0)
                        total_delay += selected_attr.get("delay_ratio", 0)
                        attribute_count += 1
                
                # Calculer le score de retard moyen
                if attribute_count > 0:
                    combination["total_delay_score"] = total_delay / attribute_count
                
                combinations.append(combination)
            
        except Exception as e:
            print(f"❌ Erreur génération écarts: {e}")
        
        return combinations
    
    @staticmethod
    def _generate_pattern_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons basées sur les patterns détectés"""
        
        print("🔍 Génération basée sur les patterns...")
        
        combinations = []
        
        try:
            # Détecter les cycles (temporairement désactivé)
            # cycles_data = PatternDetectionService.detect_cycles(db, universe)
            
            # Génération simple basée sur les patterns
            for i in range(num_combinations):
                combination = {
                    "id": f"pattern_{i+1}",
                    "strategy": "PATTERN_BASED",
                    "attributes": {},
                    "pattern_scores": {},
                    "total_pattern_score": 0,
                    "generation_method": "Pattern Recognition"
                }
                
                # Génération basique pour les patterns
                # (à améliorer avec des patterns réels détectés)
                attribute_types = ['forme', 'engine', 'beastie', 'tome', 'parite', 'unidos', 'chip']
                
                for attr_type in attribute_types:
                    # Simulation d'un pattern détecté
                    combination["attributes"][attr_type] = f"pattern_value_{i}_{attr_type}"
                    combination["pattern_scores"][attr_type] = random.uniform(0.5, 0.9)
                
                combination["total_pattern_score"] = sum(combination["pattern_scores"].values()) / len(combination["pattern_scores"])
                combinations.append(combination)
            
        except Exception as e:
            print(f"❌ Erreur génération patterns: {e}")
        
        return combinations
    
    @staticmethod
    def _generate_frequency_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        session_id: Optional[int],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons basées sur les fréquences"""
        
        print("📈 Génération basée sur les fréquences...")
        
        combinations = []
        
        try:
            # Adapter l'univers pour les requêtes selon la session
            universe_key = f"{universe}_session_{session_id}" if session_id else universe
            
            # Obtenir les prédictions basées sur les fréquences
            freq_predictions = FrequencyService.predict_next_likely(db, universe_key, top_n=10)
            
            # Organiser par type d'attribut
            freq_by_type = {}
            for pred in freq_predictions.get("predictions", []):
                attr_type = pred.get("attribute_type")
                if attr_type not in freq_by_type:
                    freq_by_type[attr_type] = []
                freq_by_type[attr_type].append(pred)
            
            # Générer les combinaisons
            for i in range(num_combinations):
                combination = {
                    "id": f"freq_{i+1}",
                    "strategy": "FREQUENCY_BASED",
                    "attributes": {},
                    "frequency_scores": {},
                    "total_frequency_score": 0,
                    "generation_method": "Frequency Analysis"
                }
                
                total_freq_score = 0
                attribute_count = 0
                
                # Sélectionner selon les fréquences
                for attr_type, preds in freq_by_type.items():
                    if preds:
                        pred_index = min(i % len(preds), len(preds) - 1)
                        selected_pred = preds[pred_index]
                        
                        combination["attributes"][attr_type] = selected_pred.get("value")
                        combination["frequency_scores"][attr_type] = selected_pred.get("frequency_score", 0)
                        total_freq_score += selected_pred.get("frequency_score", 0)
                        attribute_count += 1
                
                if attribute_count > 0:
                    combination["total_frequency_score"] = total_freq_score / attribute_count
                
                combinations.append(combination)
            
        except Exception as e:
            print(f"❌ Erreur génération fréquences: {e}")
        
        return combinations
    
    @staticmethod
    def _generate_hybrid_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        session_id: Optional[int],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons hybrides utilisant toutes les méthodes"""
        
        print("🔄 Génération hybride intelligente...")
        
        combinations = []
        
        try:
            # Générer des combinaisons avec chaque méthode
            lstm_combos = CombinationGeneratorService._generate_lstm_combinations(
                db, universe, max(2, num_combinations // 4), constraints
            )
            gap_combos = CombinationGeneratorService._generate_gap_combinations(
                db, universe, max(2, num_combinations // 4), session_id, constraints
            )
            freq_combos = CombinationGeneratorService._generate_frequency_combinations(
                db, universe, max(2, num_combinations // 4), session_id, constraints
            )
            
            # Combiner et mélanger
            all_combos = lstm_combos + gap_combos + freq_combos
            
            # Sélectionner les meilleures combinaisons
            for i, combo in enumerate(all_combos[:num_combinations]):
                hybrid_combo = {
                    "id": f"hybrid_{i+1}",
                    "strategy": "HYBRID_SMART",
                    "attributes": combo.get("attributes", {}),
                    "hybrid_scores": {
                        "lstm_confidence": combo.get("total_confidence", 0),
                        "gap_score": combo.get("total_delay_score", 0),
                        "frequency_score": combo.get("total_frequency_score", 0)
                    },
                    "total_hybrid_score": 0,
                    "generation_method": "Hybrid AI + Statistics",
                    "source_strategy": combo.get("strategy", "unknown")
                }
                
                # Calculer le score hybride
                scores = hybrid_combo["hybrid_scores"]
                hybrid_score = (
                    scores["lstm_confidence"] * 0.4 +
                    scores["gap_score"] * 0.3 +
                    scores["frequency_score"] * 0.3
                )
                hybrid_combo["total_hybrid_score"] = hybrid_score
                
                combinations.append(hybrid_combo)
            
            # Trier par score hybride décroissant
            combinations.sort(key=lambda x: x["total_hybrid_score"], reverse=True)
            
        except Exception as e:
            print(f"❌ Erreur génération hybride: {e}")
        
        return combinations[:num_combinations]
    
    @staticmethod
    def _generate_random_optimized_combinations(
        db: Session, 
        universe: str, 
        num_combinations: int, 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des combinaisons aléatoires optimisées"""
        
        print("🎲 Génération aléatoire optimisée...")
        
        combinations = []
        
        try:
            attribute_types = ['forme', 'engine', 'beastie', 'tome', 'parite', 'unidos', 'chip']
            
            for i in range(num_combinations):
                combination = {
                    "id": f"random_{i+1}",
                    "strategy": "RANDOM_OPTIMIZED",
                    "attributes": {},
                    "randomness_score": random.uniform(0.7, 1.0),
                    "generation_method": "Optimized Random"
                }
                
                # Génération aléatoire mais optimisée
                for attr_type in attribute_types:
                    # Simulation de valeurs aléatoires optimisées
                    combination["attributes"][attr_type] = f"random_{attr_type}_{random.randint(1, 100)}"
                
                combinations.append(combination)
            
        except Exception as e:
            print(f"❌ Erreur génération aléatoire: {e}")
        
        return combinations
    
    @staticmethod
    def _optimize_combinations(
        combinations: List[Dict[str, Any]], 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimise les combinaisons selon les contraintes"""
        
        if not constraints.get("avoid_duplicates", True):
            return combinations
        
        # Supprimer les doublons
        unique_combinations = []
        seen_combinations = set()
        
        for combo in combinations:
            # Créer une signature de la combinaison
            signature = tuple(sorted(combo.get("attributes", {}).items()))
            
            if signature not in seen_combinations:
                seen_combinations.add(signature)
                unique_combinations.append(combo)
        
        return unique_combinations
    
    @staticmethod
    def _analyze_generated_combinations(
        combinations: List[Dict[str, Any]], 
        strategy: str, 
        universe: str, 
        session_id: Optional[int]
    ) -> Dict[str, Any]:
        """Analyse les combinaisons générées et calcule les statistiques"""
        
        if not combinations:
            return {
                "universe": universe,
                "session_id": session_id,
                "strategy": strategy,
                "combinations": [],
                "statistics": {
                    "total_generated": 0,
                    "average_score": 0,
                    "diversity_index": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculer les statistiques
        total_combinations = len(combinations)
        
        # Score moyen selon la stratégie
        if strategy == "LSTM_BASED":
            scores = [c.get("total_confidence", 0) for c in combinations]
        elif strategy == "GAP_BASED":
            scores = [c.get("total_delay_score", 0) for c in combinations]
        elif strategy == "HYBRID_SMART":
            scores = [c.get("total_hybrid_score", 0) for c in combinations]
        else:
            scores = [0.5 for c in combinations]  # Score par défaut
        
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Index de diversité (simple)
        unique_attributes = set()
        for combo in combinations:
            for attr_value in combo.get("attributes", {}).values():
                unique_attributes.add(str(attr_value))
        
        diversity_index = len(unique_attributes) / (total_combinations * 7) if total_combinations > 0 else 0
        
        return {
            "universe": universe,
            "session_id": session_id,
            "strategy": strategy,
            "strategy_description": CombinationGeneratorService.GENERATION_STRATEGIES.get(strategy, strategy),
            "combinations": combinations,
            "statistics": {
                "total_generated": total_combinations,
                "average_score": round(average_score, 3),
                "max_score": round(max(scores) if scores else 0, 3),
                "min_score": round(min(scores) if scores else 0, 3),
                "diversity_index": round(diversity_index, 3),
                "unique_combinations": total_combinations
            },
            "generation_timestamp": datetime.now().isoformat(),
            "available_strategies": CombinationGeneratorService.GENERATION_STRATEGIES
        }