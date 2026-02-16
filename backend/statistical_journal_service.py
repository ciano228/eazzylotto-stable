"""
Service de Journal Statistique
Génère le journal détaillé pour chaque résultat de tirage
"""

from typing import Dict, List, Any, Tuple
from itertools import combinations
import psycopg2

class StatisticalJournalService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def generate_journal(self, universe: str, numbers: List[int]) -> Dict[str, Any]:
        """Génère le journal statistique complet pour un tirage"""
        
        # 1. Générer toutes les combinaisons 2 à 2
        combos = list(combinations(numbers, 2))
        
        # 2. Mapper chaque combinaison aux données Katula
        journal_entries = []
        
        for combo in combos:
            entry = self._process_combination(universe, combo, numbers)
            journal_entries.append(entry)
        
        # 3. Analyser par caractère
        character_analysis = self._analyze_by_characters(journal_entries)
        
        # 4. Générer les zones de marquage
        marking_zones = self._generate_marking_zones(journal_entries, character_analysis)
        
        return {
            'input_numbers': numbers,
            'universe': universe,
            'total_combinations': len(combos),
            'journal_entries': journal_entries,
            'character_analysis': character_analysis,
            'marking_zones': marking_zones,
            'katula_mapping': self._generate_katula_mapping(marking_zones)
        }
    
    def _process_combination(self, universe: str, combo: Tuple[int, int], 
                           original_numbers: List[int]) -> Dict[str, Any]:
        """Traite une combinaison et récupère ses données Katula"""
        num1, num2 = combo
        
        if self.use_db:
            return self._get_combination_from_db(universe, combo)
        else:
            # Mode simulation
            return self._simulate_combination_data(combo, original_numbers)
    
    def _simulate_combination_data(self, combo: Tuple[int, int], 
                                 original_numbers: List[int]) -> Dict[str, Any]:
        """Simule les données d'une combinaison"""
        num1, num2 = combo
        
        # Position géométrique simulée
        ligne = (num1 % 8) + 1
        colonne = (num2 % 6) + 1
        chip_id = ((ligne - 1) * 6) + colonne
        
        return {
            'combination': combo,
            'numbers': [num1, num2],
            'chip_id': f"chip{chip_id}",
            'denomination': f"combo_{num1}_{num2}",
            'geometric_position': {
                'ligne': ligne,
                'colonne': colonne,
                'coordinates': f"{ligne}{colonne}"
            },
            'attributes': {
                'tome': f"tome{((num1 + num2) % 4) + 1}",
                'granque': f"Q{((num1 + num2) % 6) + 1}",
                'forme': ['carre', 'triangle', 'cercle', 'rectangle'][num1 % 4],
                'petique': f"petique_{num2 % 3 + 1}"
            },
            'quadrant': self._get_quadrant(ligne, colonne),
            'zone': self._get_zone(ligne, colonne),
            'is_simulated': True
        }
    
    def _analyze_by_characters(self, journal_entries: List[Dict]) -> Dict[str, Any]:
        """Analyse les entrées par caractère"""
        analysis = {
            'tome': {},
            'forme': {},
            'granque': {},
            'quadrant': {},
            'zone': {},
            'chip': {}
        }
        
        for entry in journal_entries:
            attrs = entry['attributes']
            
            # Tome
            tome = attrs['tome']
            if tome not in analysis['tome']:
                analysis['tome'][tome] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['tome'][tome]['count'] += 1
            analysis['tome'][tome]['positions'].append(entry['geometric_position'])
            analysis['tome'][tome]['combinations'].append(entry['combination'])
            
            # Forme
            forme = attrs['forme']
            if forme not in analysis['forme']:
                analysis['forme'][forme] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['forme'][forme]['count'] += 1
            analysis['forme'][forme]['positions'].append(entry['geometric_position'])
            analysis['forme'][forme]['combinations'].append(entry['combination'])
            
            # Granque
            granque = attrs['granque']
            if granque not in analysis['granque']:
                analysis['granque'][granque] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['granque'][granque]['count'] += 1
            analysis['granque'][granque]['positions'].append(entry['geometric_position'])
            analysis['granque'][granque]['combinations'].append(entry['combination'])
            
            # Quadrant
            quadrant = entry['quadrant']
            if quadrant not in analysis['quadrant']:
                analysis['quadrant'][quadrant] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['quadrant'][quadrant]['count'] += 1
            analysis['quadrant'][quadrant]['positions'].append(entry['geometric_position'])
            analysis['quadrant'][quadrant]['combinations'].append(entry['combination'])
            
            # Zone
            zone = entry['zone']
            if zone not in analysis['zone']:
                analysis['zone'][zone] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['zone'][zone]['count'] += 1
            analysis['zone'][zone]['positions'].append(entry['geometric_position'])
            analysis['zone'][zone]['combinations'].append(entry['combination'])
            
            # Chip
            chip = entry['chip_id']
            if chip not in analysis['chip']:
                analysis['chip'][chip] = {'count': 0, 'positions': [], 'combinations': []}
            analysis['chip'][chip]['count'] += 1
            analysis['chip'][chip]['positions'].append(entry['geometric_position'])
            analysis['chip'][chip]['combinations'].append(entry['combination'])
        
        return analysis
    
    def _generate_marking_zones(self, journal_entries: List[Dict], 
                              character_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les zones de marquage pour chaque caractère"""
        marking_zones = {}
        
        for char_type, char_data in character_analysis.items():
            marking_zones[char_type] = {}
            
            for char_value, data in char_data.items():
                # Calculer les chips à marquer pour ce caractère
                chips_to_mark = set()
                
                for pos in data['positions']:
                    ligne, colonne = pos['ligne'], pos['colonne']
                    chip_num = ((ligne - 1) * 6) + colonne
                    chips_to_mark.add(chip_num)
                
                marking_zones[char_type][char_value] = {
                    'chips_to_mark': list(chips_to_mark),
                    'count': data['count'],
                    'positions': data['positions'],
                    'combinations': data['combinations'],
                    'coverage_percent': (len(chips_to_mark) / 48) * 100
                }
        
        return marking_zones
    
    def _generate_katula_mapping(self, marking_zones: Dict[str, Any]) -> Dict[str, Any]:
        """Génère le mapping pour les tables Katula"""
        katula_mapping = {}
        
        for char_type, char_data in marking_zones.items():
            katula_mapping[char_type] = {}
            
            # Créer une grille 8x6 pour chaque caractère
            for char_value, data in char_data.items():
                grid = [[False for _ in range(6)] for _ in range(8)]
                
                # Marquer les positions actives
                for chip_num in data['chips_to_mark']:
                    if 1 <= chip_num <= 48:
                        ligne = ((chip_num - 1) // 6)
                        colonne = (chip_num - 1) % 6
                        if 0 <= ligne < 8 and 0 <= colonne < 6:
                            grid[ligne][colonne] = True
                
                katula_mapping[char_type][char_value] = {
                    'grid': grid,
                    'active_chips': data['chips_to_mark'],
                    'count': data['count'],
                    'coverage': data['coverage_percent']
                }
        
        return katula_mapping
    
    def generate_period_comparison(self, universe: str, 
                                 period_draws: List[List[int]]) -> Dict[str, Any]:
        """Génère la comparaison entre plusieurs tirages d'une période"""
        
        period_journals = []
        
        # Générer le journal pour chaque tirage
        for i, numbers in enumerate(period_draws):
            journal = self.generate_journal(universe, numbers)
            journal['draw_index'] = i
            journal['draw_name'] = f"Tirage_{i+1}"
            period_journals.append(journal)
        
        # Analyser les patterns entre tirages
        cross_analysis = self._analyze_cross_period_patterns(period_journals)
        
        # Générer les tables comparatives
        comparative_tables = self._generate_comparative_tables(period_journals, cross_analysis)
        
        return {
            'universe': universe,
            'period_draws': period_draws,
            'total_draws': len(period_draws),
            'individual_journals': period_journals,
            'cross_analysis': cross_analysis,
            'comparative_tables': comparative_tables
        }
    
    def _analyze_cross_period_patterns(self, period_journals: List[Dict]) -> Dict[str, Any]:
        """Analyse les patterns croisés entre tirages"""
        patterns = {
            'recurring_tomes': {},
            'recurring_formes': {},
            'recurring_positions': {},
            'stability_index': {}
        }
        
        # Analyser les récurrences de tomes
        all_tomes = {}
        for journal in period_journals:
            for tome, data in journal['character_analysis']['tome'].items():
                if tome not in all_tomes:
                    all_tomes[tome] = []
                all_tomes[tome].append(data['count'])
        
        for tome, counts in all_tomes.items():
            if len(counts) >= 2:  # Apparaît dans au moins 2 tirages
                patterns['recurring_tomes'][tome] = {
                    'appearances': len(counts),
                    'total_count': sum(counts),
                    'avg_count': sum(counts) / len(counts),
                    'stability': 1 - (max(counts) - min(counts)) / max(counts) if max(counts) > 0 else 0
                }
        
        return patterns
    
    def _generate_comparative_tables(self, period_journals: List[Dict], 
                                   cross_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les tables comparatives pour visualisation"""
        
        tables = {}
        
        # Table par tome
        tables['tome_comparison'] = self._create_character_comparison_table(
            period_journals, 'tome'
        )
        
        # Table par forme
        tables['forme_comparison'] = self._create_character_comparison_table(
            period_journals, 'forme'
        )
        
        # Table par quadrant
        tables['quadrant_comparison'] = self._create_character_comparison_table(
            period_journals, 'quadrant'
        )
        
        return tables

    def generate_staking_strategy(self, universe: str,
                                  period_draws: List[List[int]],
                                  char_type: str = 'tome',
                                  multiplier: int = 10,
                                  max_rounds: int = 4,
                                  starting_stake: int = 1,
                                  reward_per_win: int = 200,
                                  top_n: int = 10) -> Dict[str, Any]:
        """Génère une stratégie de mise multi-tirages pour les caractères récurrents.

        - Calcule la probabilité empirique d'apparition d'un caractère par tirage
          sur la période fournie.
        - Simule une séquence de mises: stake, stake*multiplier, ... jusqu'à
          `max_rounds` et calcule l'espérance de gain, ROI, et risque de perte
          totale (pas de victoire après `max_rounds`).
        """

        if not period_draws:
            return {'status': 'error', 'message': 'No period draws provided'}

        # Générer les journaux pour chaque tirage
        period_report = self.generate_period_comparison(universe, period_draws)
        total_draws = period_report['total_draws']

        # Collecter l'apparition par caractère (nombre de tirages où il apparaît)
        char_counts = {}
        for journal in period_report['individual_journals']:
            chars = journal['character_analysis'].get(char_type, {})
            for ch, data in chars.items():
                if ch not in char_counts:
                    char_counts[ch] = 0
                if data.get('count', 0) > 0:
                    char_counts[ch] += 1

        # Prepare stakes progression
        def _stakes_sequence(s0: int, mult: int, rounds: int):
            seq = []
            s = s0
            for _ in range(rounds):
                seq.append(s)
                s = s * mult
            return seq

        def _compute_expected_profit(p: float, stakes: List[int], reward: int):
            # prob win at round i = (1-p)^i * p  (i starting at 0)
            expected = 0.0
            cum_stakes = 0
            prob_no_win = (1 - p) ** len(stakes)
            for i, stake in enumerate(stakes):
                cum_stakes += stake
                prob_win_at_i = (1 - p) ** i * p
                net_if_win = reward - cum_stakes
                expected += prob_win_at_i * net_if_win

            # account for complete failure (lose all stakes)
            expected -= prob_no_win * sum(stakes)
            return expected, prob_no_win

        results = []
        stakes_seq = _stakes_sequence(starting_stake, multiplier, max_rounds)

        for ch, appearances in char_counts.items():
            p = appearances / total_draws if total_draws > 0 else 0.0
            expected_profit, prob_no_win = _compute_expected_profit(p, stakes_seq, reward_per_win)
            total_investment_if_full = sum(stakes_seq)
            expected_roi = (expected_profit / total_investment_if_full * 100) if total_investment_if_full > 0 else 0.0

            results.append({
                'character_type': char_type,
                'character': ch,
                'appearances': appearances,
                'period_draws': total_draws,
                'empirical_probability_per_draw': round(p, 6),
                'stakes_sequence': stakes_seq,
                'total_investment_if_full': total_investment_if_full,
                'probability_no_win_after_rounds': round(prob_no_win, 6),
                'expected_profit': round(expected_profit, 2),
                'expected_roi_percent': round(expected_roi, 2)
            })

        # Trier par expected_profit décroissant et limiter
        results.sort(key=lambda x: x['expected_profit'], reverse=True)

        return {
            'status': 'success',
            'universe': universe,
            'char_type': char_type,
            'total_draws': total_draws,
            'multiplier': multiplier,
            'max_rounds': max_rounds,
            'starting_stake': starting_stake,
            'reward_per_win': reward_per_win,
            'top_n': top_n,
            'strategies': results[:top_n]
        }
    
    def _create_character_comparison_table(self, period_journals: List[Dict], 
                                         char_type: str) -> Dict[str, Any]:
        """Crée une table de comparaison pour un caractère"""
        
        # Collecter tous les caractères uniques
        all_chars = set()
        for journal in period_journals:
            all_chars.update(journal['character_analysis'][char_type].keys())
        
        # Créer la matrice de comparaison
        comparison_matrix = {}
        
        for char in all_chars:
            comparison_matrix[char] = []
            
            for journal in period_journals:
                char_data = journal['character_analysis'][char_type].get(char, {})
                count = char_data.get('count', 0)
                positions = char_data.get('positions', [])
                
                comparison_matrix[char].append({
                    'draw_name': journal['draw_name'],
                    'count': count,
                    'positions': len(positions),
                    'active': count > 0
                })
        
        return {
            'character_type': char_type,
            'comparison_matrix': comparison_matrix,
            'total_characters': len(all_chars),
            'total_draws': len(period_journals)
        }
    
    def _get_quadrant(self, ligne: int, colonne: int) -> str:
        """Détermine le quadrant"""
        if ligne <= 4 and colonne <= 3:
            return "Q1"
        elif ligne <= 4 and colonne > 3:
            return "Q2"
        elif ligne > 4 and colonne <= 3:
            return "Q3"
        else:
            return "Q4"
    
    def _get_zone(self, ligne: int, colonne: int) -> str:
        """Détermine la zone géométrique"""
        if ligne <= 3:
            v_zone = "top"
        elif ligne <= 6:
            v_zone = "middle"
        else:
            v_zone = "bottom"
        
        if colonne <= 2:
            h_zone = "left"
        elif colonne <= 4:
            h_zone = "center"
        else:
            h_zone = "right"
        
        return f"{v_zone}_{h_zone}"

    def get_period_stats(self, journal_data: List[Dict]) -> Dict[int, Dict[str, Dict[str, int]]]:
        """
        Génère des statistiques agrégées par période pour tous les attributs.
        Structure: { period: { attr: { value: count } } }
        """
        period_stats = {}
        for entry in journal_data:
            period = entry.get('period')
            if period is None: continue
            
            if period not in period_stats:
                period_stats[period] = {}
            
            # Attributs simples
            simple_attrs = ['forme', 'engine', 'beastie', 'tome', 'granque', 'petique', 'ligne', 'colonne', 'chip']
            for attr in simple_attrs:
                val = entry.get(attr)
                if val:
                    if attr not in period_stats[period]:
                        period_stats[period][attr] = {}
                    period_stats[period][attr][val] = period_stats[period][attr].get(val, 0) + 1
        return period_stats

    def find_missing_attribute_periods(self, journal_data: List[Dict], attr: str, value: str) -> List[int]:
        """Trouve les périodes où un attribut spécifique n'est jamais apparu."""
        period_stats = self.get_period_stats(journal_data)
        missing_periods = []
        for period, stats in period_stats.items():
            attr_stats = stats.get(attr, {})
            if value not in attr_stats:
                missing_periods.append(period)
        return sorted(missing_periods)

    def find_attribute_value_count_periods(self, journal_data: List[Dict], attr: str, value: str, target_count: int = 0) -> List[int]:
        """Trouve les périodes où un attribut a un nombre d'occurrences spécifique."""
        period_stats = self.get_period_stats(journal_data)
        matching_periods = []
        for period, stats in period_stats.items():
            count = stats.get(attr, {}).get(value, 0)
            if count == target_count:
                matching_periods.append(period)
        return sorted(matching_periods)

    def get_most_regular_attribute(self, journal_data: List[Dict], attr_list: List[str]) -> Dict[str, Any]:
        """
        Détermine l'attribut le plus régulier (celui dont l'écart-type de la fréquence par période est le plus faible).
        """
        period_stats = self.get_period_stats(journal_data)
        if not period_stats: return {}
        
        regularity_scores = []
        for attr in attr_list:
            # Calculer les fréquences par période
            counts = []
            for period in sorted(period_stats.keys()):
                total_per_period = sum(period_stats[period].get(attr, {}).values())
                if total_per_period > 0:
                    counts.append(sum(1 for v in period_stats[period].get(attr, {}).values() if v > 0)) # Variété
                else:
                    counts.append(0)
            
            if not counts: continue
            
            # Calculer la variance simplifiée
            avg = sum(counts) / len(counts)
            variance = sum((c - avg) ** 2 for c in counts) / len(counts)
            
            regularity_scores.append({
                'attribute': attr,
                'score': variance,
                'avg_variety': avg
            })
            
        if not regularity_scores: return {}
        
        # Le score le plus bas est le plus régulier
        regularity_scores.sort(key=lambda x: x['score'])
        return regularity_scores[0]