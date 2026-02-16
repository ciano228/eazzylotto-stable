"""
Service de Zones Synthétiques et Analyse Prédictive Avancée
"""
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import psycopg2
from collections import defaultdict, Counter
import json
import hashlib

@dataclass
class HistoricalResult:
    """Résultat historique pour analyse des patterns"""
    date: datetime
    winning_combination: str
    petique: str
    granque: str
    tome: str
    ligne: int
    colonne: int
    forme: str
    chip: str
    denomination: str

@dataclass
class SyntheticZone:
    """Zone synthétique créée par combinaison de zones naturelles"""
    zone_id: str
    name: str
    description: str
    component_zones: List[Dict[str, Any]]  # Zones composantes
    total_combinations: int
    frequency_score: float  # Fréquence d'apparition historique
    pattern_strength: float  # Force du pattern détecté
    investment_cost: int
    expected_roi: float
    confidence_level: str  # HIGH, MEDIUM, LOW
    last_occurrence: Optional[datetime]
    occurrence_count: int
    creation_logic: str  # Explication de la logique de création

@dataclass
class PatternAnalysis:
    """Analyse de pattern pour une zone"""
    zone_identifier: str
    pattern_type: str  # CYCLIQUE, TENDANCE, ALEATOIRE
    frequency: float  # Occurrences par période
    last_occurrences: List[datetime]
    next_predicted: Optional[datetime]
    confidence: float  # 0-100%
    trend_direction: str  # CROISSANT, DECROISSANT, STABLE

class SyntheticZonesService:
    """Service d'analyse prédictive et création de zones synthétiques"""
    
    def __init__(self):
        from katula_complete_service import KatulaCompleteService
        self.katula_service = KatulaCompleteService()
        self.db_config = self.katula_service.db_config
        
        # Paramètres d'analyse
        self.MIN_FREQUENCY_THRESHOLD = 0.15  # 15% minimum de fréquence
        self.MIN_PATTERN_STRENGTH = 0.6      # 60% minimum de force de pattern
        self.ANALYSIS_PERIOD_DAYS = 90       # Période d'analyse en jours
        
    def analyze_historical_patterns(self, universe: str, days_back: int = 90) -> List[PatternAnalysis]:
        """Analyse les patterns historiques pour toutes les zones"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer l'historique des résultats (simulation pour l'exemple)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Pour l'instant, on simule des données historiques
            # Dans un vrai système, on aurait une table 'historical_results'
            historical_data = self._generate_simulated_history(universe, days_back)
            
            patterns = []
            
            # Analyser chaque type de zone
            zone_types = ['petique', 'granque', 'tome', 'ligne', 'colonne']
            
            for zone_type in zone_types:
                zone_patterns = self._analyze_zone_type_patterns(historical_data, zone_type)
                patterns.extend(zone_patterns)
            
            cursor.close()
            conn.close()
            
            return patterns
            
        except Exception as e:
            print(f"[ERROR] analyze_historical_patterns: {e}")
            return []
    
    def create_synthetic_zones(self, universe: str, min_frequency: float = 0.2) -> List[SyntheticZone]:
        """Crée des zones synthétiques basées sur l'analyse des patterns"""
        try:
            # Analyser les patterns existants
            patterns = self.analyze_historical_patterns(universe)
            
            # Récupérer les données de base
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            synthetic_zones = []
            
            # 1. Zones par intersection de critères multiples
            intersection_zones = self._create_intersection_zones(cursor, universe)
            synthetic_zones.extend(intersection_zones)
            
            # 2. Zones par clusters de fréquence
            frequency_zones = self._create_frequency_clusters(cursor, universe, patterns)
            synthetic_zones.extend(frequency_zones)
            
            # 3. Zones par patterns temporels
            temporal_zones = self._create_temporal_pattern_zones(cursor, universe, patterns)
            synthetic_zones.extend(temporal_zones)
            
            # 4. Zones par corrélations découvertes
            correlation_zones = self._create_correlation_zones(cursor, universe)
            synthetic_zones.extend(correlation_zones)
            
            cursor.close()
            conn.close()
            
            # Filtrer et trier par rentabilité
            profitable_zones = [z for z in synthetic_zones if z.expected_roi > 5.0]
            profitable_zones.sort(key=lambda x: x.expected_roi, reverse=True)
            
            return profitable_zones[:20]  # Top 20 zones synthétiques
            
        except Exception as e:
            print(f"[ERROR] create_synthetic_zones: {e}")
            return []
    
    def _create_intersection_zones(self, cursor, universe: str) -> List[SyntheticZone]:
        """Crée des zones par intersection de critères (ex: Tome1 ∩ Q1 ∩ Forme_Carré)"""
        zones = []
        
        try:
            # Exemple: Intersection Tome + Granque
            cursor.execute("""
                SELECT t.tome, g.granque_name, COUNT(DISTINCT c.combination) as combo_count,
                       AVG(CASE WHEN c.alpha_ranking <= 'f' THEN 1.0 ELSE 0.5 END) as freq_score
                FROM combinations c
                JOIN combinations t ON c.univers = t.univers AND c.chip = t.chip
                JOIN combinations g ON c.univers = g.univers AND c.chip = g.chip
                WHERE c.univers = %s AND t.tome IS NOT NULL AND g.granque_name IS NOT NULL
                GROUP BY t.tome, g.granque_name
                HAVING COUNT(DISTINCT c.combination) BETWEEN 15 AND 80
                ORDER BY freq_score DESC, combo_count ASC
                LIMIT 10
            """, (universe,))
            
            results = cursor.fetchall()
            
            for tome, granque, combo_count, freq_score in results:
                zone_id = f"SYNTH_TG_{tome}_{granque}"
                
                zone = SyntheticZone(
                    zone_id=zone_id,
                    name=f"Intersection {tome.upper()} × {granque}",
                    description=f"Zone synthétique combinant {tome} et {granque}",
                    component_zones=[
                        {"type": "tome", "value": tome},
                        {"type": "granque", "value": granque}
                    ],
                    total_combinations=combo_count,
                    frequency_score=freq_score,
                    pattern_strength=min(freq_score * 1.2, 1.0),
                    investment_cost=combo_count,
                    expected_roi=((200 - combo_count) / combo_count * 100) if combo_count > 0 else 0,
                    confidence_level="HIGH" if freq_score > 0.7 else "MEDIUM",
                    last_occurrence=datetime.now() - timedelta(days=2),
                    occurrence_count=int(freq_score * 30),
                    creation_logic=f"Intersection fréquente entre {tome} et {granque} avec {combo_count} combinaisons"
                )
                
                if zone.expected_roi > 0:
                    zones.append(zone)
                    
        except Exception as e:
            print(f"[ERROR] _create_intersection_zones: {e}")
        
        return zones
    
    def _create_frequency_clusters(self, cursor, universe: str, patterns: List[PatternAnalysis]) -> List[SyntheticZone]:
        """Crée des zones basées sur les clusters de fréquence élevée"""
        zones = []
        
        try:
            # Identifier les dénominations les plus fréquentes
            cursor.execute("""
                SELECT denomination, COUNT(*) as freq, 
                       STRING_AGG(DISTINCT chip, ',') as chips,
                       STRING_AGG(DISTINCT forme, ',') as formes
                FROM combinations 
                WHERE univers = %s 
                GROUP BY denomination 
                HAVING COUNT(*) >= 3
                ORDER BY freq DESC
                LIMIT 15
            """, (universe,))
            
            results = cursor.fetchall()
            
            for denom, freq, chips_str, formes_str in results:
                chips = chips_str.split(',')
                formes = formes_str.split(',')
                
                # Créer une zone synthétique pour cette dénomination fréquente
                zone_id = f"SYNTH_FREQ_{hashlib.md5(denom.encode()).hexdigest()[:8]}"
                
                zone = SyntheticZone(
                    zone_id=zone_id,
                    name=f"Cluster-Freq: {denom[:20]}...",
                    description=f"Zone synthétique basée sur la fréquence élevée de '{denom}'",
                    component_zones=[
                        {"type": "denomination", "value": denom},
                        {"type": "chips", "value": chips[:5]},  # Limiter à 5 chips
                        {"type": "formes", "value": formes}
                    ],
                    total_combinations=min(freq * 2, 50),  # Estimation conservative
                    frequency_score=min(freq / 10.0, 1.0),
                    pattern_strength=min(freq / 8.0, 1.0),
                    investment_cost=min(freq * 2, 50),
                    expected_roi=((200 - min(freq * 2, 50)) / min(freq * 2, 50) * 100) if freq > 0 else 0,
                    confidence_level="HIGH" if freq >= 5 else "MEDIUM",
                    last_occurrence=datetime.now() - timedelta(days=1),
                    occurrence_count=freq,
                    creation_logic=f"Dénomination '{denom}' apparaît {freq} fois - pattern de fréquence élevée"
                )
                
                if zone.expected_roi > 0 and zone.investment_cost < 150:
                    zones.append(zone)
                    
        except Exception as e:
            print(f"[ERROR] _create_frequency_clusters: {e}")
        
        return zones
    
    def _create_temporal_pattern_zones(self, cursor, universe: str, patterns: List[PatternAnalysis]) -> List[SyntheticZone]:
        """Crée des zones basées sur les patterns temporels détectés"""
        zones = []
        
        # Simuler des patterns temporels découverts
        temporal_patterns = [
            {"name": "Cycle-Hebdo-Q1", "zone_type": "petique", "zone_value": "q1", "cycle_days": 7, "confidence": 0.75},
            {"name": "Trend-Tome1", "zone_type": "tome", "zone_value": "tome1", "cycle_days": 14, "confidence": 0.68},
            {"name": "Pattern-L1L2", "zone_type": "lignes", "zone_value": "L1,L2", "cycle_days": 10, "confidence": 0.72}
        ]
        
        for pattern in temporal_patterns:
            try:
                # Estimer le nombre de combinaisons pour ce pattern
                if pattern["zone_type"] == "petique":
                    combo_count = 45  # Estimation pour un quadrant
                elif pattern["zone_type"] == "tome":
                    combo_count = 35  # Estimation pour un tome
                else:
                    combo_count = 60  # Estimation pour lignes multiples
                
                zone_id = f"SYNTH_TEMP_{pattern['name']}"
                
                zone = SyntheticZone(
                    zone_id=zone_id,
                    name=f"Pattern-Temporel: {pattern['name']}",
                    description=f"Zone synthétique basée sur un cycle de {pattern['cycle_days']} jours",
                    component_zones=[
                        {"type": pattern["zone_type"], "value": pattern["zone_value"]},
                        {"type": "temporal", "cycle_days": pattern["cycle_days"]}
                    ],
                    total_combinations=combo_count,
                    frequency_score=pattern["confidence"],
                    pattern_strength=pattern["confidence"],
                    investment_cost=combo_count,
                    expected_roi=((200 - combo_count) / combo_count * 100) if combo_count > 0 else 0,
                    confidence_level="HIGH" if pattern["confidence"] > 0.7 else "MEDIUM",
                    last_occurrence=datetime.now() - timedelta(days=pattern["cycle_days"]),
                    occurrence_count=int(pattern["confidence"] * 20),
                    creation_logic=f"Pattern temporel détecté: cycle de {pattern['cycle_days']} jours avec {pattern['confidence']*100:.1f}% de confiance"
                )
                
                if zone.expected_roi > 10:  # Seuil plus élevé pour les patterns temporels
                    zones.append(zone)
                    
            except Exception as e:
                print(f"[ERROR] temporal pattern {pattern['name']}: {e}")
        
        return zones
    
    def _create_correlation_zones(self, cursor, universe: str) -> List[SyntheticZone]:
        """Crée des zones basées sur les corrélations découvertes"""
        zones = []
        
        try:
            # Découvrir des corrélations entre formes et positions
            cursor.execute("""
                SELECT forme, petique, COUNT(*) as freq,
                       COUNT(DISTINCT denomination) as unique_denoms
                FROM combinations 
                WHERE univers = %s 
                GROUP BY forme, petique
                HAVING COUNT(*) >= 5 AND COUNT(DISTINCT denomination) >= 3
                ORDER BY freq DESC
                LIMIT 8
            """, (universe,))
            
            results = cursor.fetchall()
            
            for forme, petique, freq, unique_denoms in results:
                zone_id = f"SYNTH_CORR_{forme}_{petique}"
                
                # Estimation du nombre de combinaisons
                combo_count = min(unique_denoms * 3, 80)
                
                zone = SyntheticZone(
                    zone_id=zone_id,
                    name=f"Corrélation: {forme.upper()} × {petique}",
                    description=f"Zone synthétique basée sur la corrélation {forme}-{petique}",
                    component_zones=[
                        {"type": "forme", "value": forme},
                        {"type": "petique", "value": petique}
                    ],
                    total_combinations=combo_count,
                    frequency_score=min(freq / 15.0, 1.0),
                    pattern_strength=min((freq * unique_denoms) / 50.0, 1.0),
                    investment_cost=combo_count,
                    expected_roi=((200 - combo_count) / combo_count * 100) if combo_count > 0 else 0,
                    confidence_level="MEDIUM",
                    last_occurrence=datetime.now() - timedelta(days=3),
                    occurrence_count=freq,
                    creation_logic=f"Corrélation forte entre forme '{forme}' et pétique '{petique}' ({freq} occurrences, {unique_denoms} dénominations uniques)"
                )
                
                if zone.expected_roi > 5 and zone.investment_cost < 120:
                    zones.append(zone)
                    
        except Exception as e:
            print(f"[ERROR] _create_correlation_zones: {e}")
        
        return zones
    
    def _generate_simulated_history(self, universe: str, days_back: int) -> List[HistoricalResult]:
        """Génère un historique simulé pour les tests (à remplacer par de vraies données)"""
        import random
        from datetime import datetime, timedelta
        
        history = []
        
        # Simuler des résultats historiques
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            
            # Simuler des patterns réalistes
            if i % 7 == 0:  # Pattern hebdomadaire pour q1
                petique = "q1"
                granque = "Q1"
            elif i % 14 == 0:  # Pattern bi-hebdomadaire pour tome1
                petique = random.choice(["q1", "q2"])
                granque = "Q2"
            else:
                petique = random.choice(["q1", "q2", "q3", "q4"])
                granque = random.choice(["Q1", "Q2", "Q3", "Q4"])
            
            result = HistoricalResult(
                date=date,
                winning_combination=f"{random.randint(1,48)}-{random.randint(1,48)}",
                petique=petique,
                granque=granque,
                tome=random.choice(["tome1", "tome2", "tome3"]),
                ligne=random.randint(1, 8),
                colonne=random.randint(1, 6),
                forme=random.choice(["carre", "triangle", "cercle", "rectangle"]),
                chip=f"chip{random.randint(1, 48)}",
                denomination=f"item{random.randint(1, 100)}"
            )
            
            history.append(result)
        
        return history
    
    def _analyze_zone_type_patterns(self, historical_data: List[HistoricalResult], zone_type: str) -> List[PatternAnalysis]:
        """Analyse les patterns pour un type de zone spécifique"""
        patterns = []
        
        # Compter les occurrences par zone
        zone_counts = Counter()
        zone_dates = defaultdict(list)
        
        for result in historical_data:
            if zone_type == 'petique':
                zone_value = result.petique
            elif zone_type == 'granque':
                zone_value = result.granque
            elif zone_type == 'tome':
                zone_value = result.tome
            elif zone_type == 'ligne':
                zone_value = f"L{result.ligne}"
            elif zone_type == 'colonne':
                zone_value = f"C{result.colonne}"
            else:
                continue
            
            zone_counts[zone_value] += 1
            zone_dates[zone_value].append(result.date)
        
        # Analyser chaque zone
        for zone_value, count in zone_counts.items():
            if count >= 3:  # Minimum d'occurrences pour analyse
                dates = sorted(zone_dates[zone_value], reverse=True)
                frequency = count / len(historical_data)
                
                # Déterminer le type de pattern
                if len(dates) >= 3:
                    intervals = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
                    avg_interval = sum(intervals) / len(intervals)
                    
                    if avg_interval <= 10:
                        pattern_type = "CYCLIQUE"
                        confidence = min(frequency * 100, 85)
                    elif len(set(intervals)) <= 2:
                        pattern_type = "TENDANCE"
                        confidence = min(frequency * 80, 75)
                    else:
                        pattern_type = "ALEATOIRE"
                        confidence = min(frequency * 60, 60)
                else:
                    pattern_type = "INSUFFISANT"
                    confidence = 30
                
                pattern = PatternAnalysis(
                    zone_identifier=f"{zone_type}:{zone_value}",
                    pattern_type=pattern_type,
                    frequency=frequency,
                    last_occurrences=dates[:5],
                    next_predicted=dates[0] + timedelta(days=int(avg_interval)) if len(dates) >= 2 else None,
                    confidence=confidence,
                    trend_direction="STABLE"
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def get_joker_zones(self, universe: str, max_cost: int = 50) -> List[SyntheticZone]:
        """Trouve les zones 'joker' - petites, fréquentes et très rentables"""
        synthetic_zones = self.create_synthetic_zones(universe)
        
        # Filtrer les zones joker selon les critères stricts
        joker_zones = []
        
        for zone in synthetic_zones:
            if (zone.investment_cost <= max_cost and 
                zone.frequency_score >= 0.6 and 
                zone.expected_roi >= 20 and
                zone.confidence_level in ["HIGH", "MEDIUM"]):
                
                joker_zones.append(zone)
        
        # Trier par score composite (ROI × Fréquence × Confiance)
        joker_zones.sort(key=lambda z: z.expected_roi * z.frequency_score * (1.2 if z.confidence_level == "HIGH" else 1.0), reverse=True)
        
        return joker_zones[:5]  # Top 5 zones joker