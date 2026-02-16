"""
Pattern Discovery Engine
Découvre automatiquement les combinaisons d'attributs récurrentes dans l'historique
"""

import psycopg2
from itertools import combinations
from collections import defaultdict
from typing import Dict, List, Tuple
import json
from datetime import datetime

class PatternDiscoveryEngine:
    def __init__(self, db_config):
        self.db_config = db_config
        self.pattern_counts = defaultdict(int)
        self.total_draws = 0
        self.draw_dates = []  # Pour analyse de régularité
        
    def explore_all_sessions(self, universe='mundo', min_frequency_percent=10, session_id=None):
        """
        Analyse toutes les sessions pour découvrir les patterns
        
        Args:
            universe: L'univers à analyser
            min_frequency_percent: Fréquence minimale pour inclure un pattern dans le rapport
            session_id: Optionnel - filtre par session spécifique
        
        Returns:
            Dict avec les patterns découverts
        """
        print(f"\n{'='*60}")
        print(f"PATTERN DISCOVERY ENGINE - Universe: {universe}")
        if session_id:
            print(f"Session Filter: {session_id}")
        print(f"{'='*60}\n")
        
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Récupérer tous les tirages complétés
        print("Chargement des tirages...")
        
        if session_id:
            cur.execute("""
                SELECT winning_numbers, draw_date
                FROM session_draws 
                WHERE session_id = %s
                  AND jsonb_array_length(winning_numbers::jsonb) > 0
                  AND is_completed = TRUE
                ORDER BY draw_date
            """, (session_id,))
        else:
            cur.execute("""
                SELECT winning_numbers, draw_date
                FROM session_draws 
                WHERE jsonb_array_length(winning_numbers::jsonb) > 0
                  AND is_completed = TRUE
                ORDER BY draw_date
            """)
        
        draws = cur.fetchall()
        print(f"Tirages trouves: {len(draws)}")
        
        # Analyser chaque tirage
        for i, (numbers, draw_date) in enumerate(draws, 1):
            if i % 100 == 0:
                print(f"  Progression: {i}/{len(draws)} tirages analyses...")
            
            self.analyze_draw(numbers, universe)
            self.total_draws += 1
            if draw_date:
                self.draw_dates.append(draw_date)
        
        conn.close()
        
        print(f"\nAnalyse terminee: {self.total_draws} tirages")
        print(f"Patterns uniques detectes: {len(self.pattern_counts)}")
        
        return self.generate_report(min_frequency_percent)
    
    def analyze_draw(self, winning_numbers: List[int], universe: str):
        """
        Extrait tous les patterns d'un tirage
        """
        # Convertir winning_numbers si c'est une string JSON
        if isinstance(winning_numbers, str):
            import json
            winning_numbers = json.loads(winning_numbers)
        
        # Pour chaque paire de numéros dans ce tirage
        for pair in combinations(winning_numbers, 2):
            # Récupérer les attributs de cette paire
            attrs = self.get_pair_attributes(pair, universe)
            
            if not attrs:
                continue
            
            # Générer patterns de différentes tailles
            self._generate_patterns(attrs)
    
    def _generate_patterns(self, attrs: Dict[str, str]):
        """
        Génère tous les patterns possibles à partir des attributs
        """
        attr_items = list(attrs.items())
        
        # Patterns simples (1 attribut)
        for k, v in attr_items:
            if v:  # Ignorer valeurs nulles
                self.pattern_counts[f"{k}:{v}"] += 1
        
        # Patterns 2 attributs
        for combo in combinations(attr_items, 2):
            pattern_parts = [f"{k}:{v}" for k, v in combo if v]
            if len(pattern_parts) == 2:
                pattern = "_".join(sorted(pattern_parts))  # Tri pour normaliser
                self.pattern_counts[pattern] += 1
        
        # Patterns 3 attributs
        for combo in combinations(attr_items, 3):
            pattern_parts = [f"{k}:{v}" for k, v in combo if v]
            if len(pattern_parts) == 3:
                pattern = "_".join(sorted(pattern_parts))
                self.pattern_counts[pattern] += 1
        
        # Patterns 4 attributs
        for combo in combinations(attr_items, 4):
            pattern_parts = [f"{k}:{v}" for k, v in combo if v]
            if len(pattern_parts) == 4:
                pattern = "_".join(sorted(pattern_parts))
                self.pattern_counts[pattern] += 1
    
    def get_pair_attributes(self, pair: Tuple[int, int], universe: str) -> Dict[str, str]:
        """
        Récupère les attributs d'une paire depuis la DB
        """
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        num1, num2 = sorted(pair)
        
        cur.execute("""
            SELECT forme, tome, granque_name, engine, petique
            FROM combinations
            WHERE univers = %s 
              AND num1 = %s 
              AND num2 = %s
            LIMIT 1
        """, (universe, num1, num2))
        
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                'forme': row[0],
                'tome': row[1],
                'granque': row[2],
                'engine': row[3],
                'petique': row[4]
            }
        return {}
    
    def generate_report(self, min_frequency_percent=10):
        """
        Génère le rapport des patterns découverts
        """
        print(f"\nGeneration du rapport (seuil: {min_frequency_percent}%)...")
        
        results = []
        
        for pattern, count in self.pattern_counts.items():
            frequency = (count / self.total_draws) * 100 if self.total_draws > 0 else 0
            
            # Filtrer patterns peu fréquents
            if frequency >= min_frequency_percent:
                # Compter nombre d'attributs dans le pattern
                num_attributes = pattern.count(':')
                
                results.append({
                    'pattern': pattern,
                    'count': count,
                    'frequency_percent': round(frequency, 2),
                    'num_attributes': num_attributes,
                    'category': self._categorize_pattern(pattern)
                })
        
        # Trier par fréquence décroissante
        results.sort(key=lambda x: x['frequency_percent'], reverse=True)
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_draws_analyzed': self.total_draws,
                'patterns_discovered': len(results),
                'min_frequency_threshold': min_frequency_percent
            },
            'top_patterns': results
        }
        
        # Afficher résumé
        print(f"\n{'='*60}")
        print(f"RAPPORT DE DECOUVERTE")
        print(f"{'='*60}")
        print(f"Tirages analyses: {self.total_draws}")
        print(f"Patterns frequents (>{min_frequency_percent}%): {len(results)}")
        print(f"\nTop 10 Patterns:")
        
        for i, p in enumerate(results[:10], 1):
            print(f"{i:2}. [{p['num_attributes']} attrs] {p['pattern'][:50]:50} -> {p['frequency_percent']:5.1f}% ({p['count']} fois)")
        
        return report
    
    def _categorize_pattern(self, pattern: str) -> str:
        """
        Catégorise un pattern selon ses attributs
        """
        if 'granque' in pattern and 'tome' in pattern:
            return 'temporal_spatial'
        elif 'forme' in pattern and 'engine' in pattern:
            return 'geometric_mobility'
        elif 'granque' in pattern:
            return 'spatial'
        elif 'forme' in pattern:
            return 'geometric'
        elif 'engine' in pattern:
            return 'mobility'
        else:
            return 'other'
    
    def save_report(self, report: Dict, filename='pattern_discovery_report.json'):
        """
        Sauvegarde le rapport dans un fichier JSON
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nRapport sauvegarde: {filename}")


def main():
    """
    Point d'entrée principal
    """
    import sys
    
    db_config = {
        'dbname': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'host': 'localhost',
        'port': '5432'
    }
    
    # Créer l'engine de découverte
    engine = PatternDiscoveryEngine(db_config)
    
    # Check for session_id argument
    session_id = None
    if len(sys.argv) > 1 and sys.argv[1] == '--session-id' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        print(f"Filtre: Session ID = {session_id}")
    
    # Explorer toutes les sessions pour 'mundo'
    # Threshold: 25% (similar to tome3 frequency of 28.59%)
    report = engine.explore_all_sessions(
        universe='mundo',
        min_frequency_percent=25,  # Patterns appearing in at least 25% of draws
        session_id=session_id
    )
    
    # Sauvegarder le rapport
    filename = f'pattern_discovery_report_session{session_id}.json' if session_id else 'pattern_discovery_report.json'
    engine.save_report(report, filename)
    
    print(f"\n{'='*60}")
    print("Exploration terminee!")
    print(f"Consultez le fichier: {filename}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
