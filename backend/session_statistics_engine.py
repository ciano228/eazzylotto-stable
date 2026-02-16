import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import psycopg2
from collections import defaultdict
import itertools

logger = logging.getLogger(__name__)

class SessionStatisticsEngine:
    """
    Moteur de statistiques avancées pour les sessions Katula.
    Calcule count, fréquence, dernière sortie, et écart (due) pour tous les attributs.
    Utilise le mapping RÉEL de la DB (table combinations).
    """

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        # Initialiser le moteur d'attributs synthétiques
        try:
            from .synthetic_attribute_engine import SyntheticAttributeEngine
            self.synthetic_engine = SyntheticAttributeEngine()
        except ImportError:
            # Fallback if not in the same package during tests
            from synthetic_attribute_engine import SyntheticAttributeEngine
            self.synthetic_engine = SyntheticAttributeEngine()

    def calculate_stats(self, session_draws: List[Dict[str, Any]], universe: str) -> Dict[str, Any]:
        """
        Calcule les statistiques complètes pour les tirages donnés dans un univers spécifique.
        """
        if not session_draws:
            return {}

        # 1. Charger le mapping (Dénomination -> Attributs) pour l'univers
        # Cela évite de faire des requêtes pour chaque numéro de chaque tirage.
        universe_map = self._load_universe_map(universe)
        if not universe_map:
            logger.warning(f"Aucune carte (map) trouvée pour l'univers {universe}")
            return {}

        # 2. Initialiser les structures de données pour les stats
        # Structure: stats[attribute_type][attribute_value] = { count, last_index, ... }
        stats = defaultdict(lambda: defaultdict(lambda: {
            "count": 0,
            "last_draw_index": -1,  # Index dans la liste inversée ou chronologique? On va utiliser l'index chronologique (0 = plus ancien)
            "last_draw_date": None,
            "dates": []
        }))

        # Trier les tirages par date (du plus ancien au plus récent) pour le calcul correct des écarts
        # On suppose que session_draws est peut-être désordonné.
        sorted_draws = sorted(session_draws, key=lambda x: x.get('draw_date') or "")
        
        total_draws = len(sorted_draws)

        # 3. Itérer sur les tirages        # 2. Map draws to attributes (PAIR-BASED ANALYSIS)
        # We generate all pairs (combinations of 2) from the draw and check if they exist in our map.
        for i, draw in enumerate(sorted_draws):
            draw_date = draw.get('draw_date')
            winning_numbers = draw.get('winning_numbers', [])
            
            # Clean and validate numbers
            valid_numbers = []
            if winning_numbers:
                for n in winning_numbers:
                    try:
                        valid_numbers.append(int(n))
                    except (ValueError, TypeError):
                        continue
            
            if len(valid_numbers) < 2:
                continue

            # Generate Pairs (sorted tuples)
            pairs = list(itertools.combinations(valid_numbers, 2))
            
            for p in pairs:
                p_key = tuple(sorted(p)) # ensure (min, max)
                
                # Check mapping
                # Mapping key is expected to be a tuple (n1, n2) or string "n1-n2"
                # Our _load_universe_map will return dict keyed by tuple (n1, n2)
                
                if p_key in universe_map:
                    attrs_list = universe_map[p_key]
                    for attrs in attrs_list:
                         # 1. Tracker les attributs atomiques (existant)
                         self._update_stats_for_attrs(stats, attrs, i, draw_date)
                         
                         # 2. Générer et tracker les attributs synthétiques (Nouveauté)
                         if hasattr(self, 'synthetic_engine'):
                             synthetic_attrs = self.synthetic_engine.synthesize(attrs)
                             if synthetic_attrs:
                                 # On utilise le même tracker pour les synthétiques
                                 # en passant les attributs générés directement
                                 self._update_synthetic_stats(stats, synthetic_attrs, i, draw_date)

        # 4. Finaliser les calculs (Fréquence, Écart Actuel)
        final_report = {}
        
        for attr_type, values_dict in stats.items():
            final_report[attr_type] = []
            
            for attr_value, data in values_dict.items():
                count = data["count"]
                last_idx = data["last_draw_index"]
                
                # Écart (Due): Nombre de tirages depuis la dernière sortie.
                # Si sorti au dernier tirage (index = total_draws - 1), écart = 0.
                # Si jamais sorti, écart = total_draws (ou une autre convention).
                if last_idx == -1:
                    ecart = total_draws
                else:
                    ecart = (total_draws - 1) - last_idx

                frequency = (count / total_draws) * 100 if total_draws > 0 else 0

                final_report[attr_type].append({
                    "value": attr_value,
                    "count": count,
                    "frequency": round(frequency, 2),
                    "last_appearance": data["last_draw_date"],
                    "due": ecart,
                    "history": data["dates"] # Optionnel, pour debug ou sparklines
                })

            # Trier par count décroissant par défaut ? Ou laisser le front trier.
            # On laisse le front trier, mais on peut trier par défaut par valeur pour être propre.
            # Attention aux types mixtes, on trie en string.
            final_report[attr_type].sort(key=lambda x: str(x['value']))

        return final_report

    def _update_stats_for_attrs(self, stats, attrs, draw_index, draw_date):
        """Met à jour les stats pour un ensemble d'attributs trouvé."""
        # Liste des clés à tracker - ÉTENDUE POUR COHÉRENCE
        keys_to_track = [
            'forme', 'tome', 'granque_name', 'petique', 
            'engine', 'beastie', 'alpha_ranking', 'chip', 'denomination',
            'parite', 'region', 'gentile', 'quartier', 'base_name'
        ]
        
        # Ajouter aussi ligne/colonne si dispo
        if 'ligne' in attrs and 'colonne' in attrs:
             l_val = attrs['ligne']
             c_val = attrs['colonne']
             
             if l_val:
                 stats['ligne'][f"L{l_val}"]["count"] += 1
                 stats['ligne'][f"L{l_val}"]["last_draw_index"] = draw_index
                 stats['ligne'][f"L{l_val}"]["last_draw_date"] = draw_date
             
             if c_val:
                 stats['colonne'][f"C{c_val}"]["count"] += 1
                 stats['colonne'][f"C{c_val}"]["last_draw_index"] = draw_index
                 stats['colonne'][f"C{c_val}"]["last_draw_date"] = draw_date

        for key in keys_to_track:
            val = attrs.get(key)
            if val and val != "---" and val != "":
                # Normalisation des clés pour l'affichage
                # ex: granque_name -> granque
                # base_name -> base_name (exception)
                if key == 'base_name':
                    report_key = key
                else:
                    report_key = key.replace('_name', '') 
                
                entry = stats[report_key][val]
                entry["count"] += 1
                entry["last_draw_index"] = draw_index
                entry["last_draw_date"] = draw_date
                # entry["dates"].append(draw_date) # désactivé pour perf si bcp de tirages

    def _load_universe_map(self, universe: str) -> Dict[Tuple[int, int], List[Dict[str, Any]]]:
        """
        Charge dynamiquement TOUTES les colonnes de la table combinations.
        Retourne Dict[(num1, num2), List[Attributes]]
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 1. Récupérer dynamiquement les noms des colonnes
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations' ORDER BY ordinal_position")
            columns = [row[0] for row in cursor.fetchall()]
            
            if not columns:
                return {}

            # Détecter la colonne univers/universe
            univ_col = "univers" if "univers" in columns else "universe"
            
            # 2. Construire la requête avec toutes les colonnes
            # MODIFICATION CRITIQUE : On ne filtre PLUS par univers.
            # On veut charger la carte complète de toutes les paires (1-90) peu importe leur univers d'origine.
            query = f"SELECT * FROM combinations"
            cursor.execute(query)
            results = cursor.fetchall()
            
            mapping = defaultdict(list)
            
            for row in results:
                # Créer un dictionnaire complet des attributs
                row_dict = dict(zip(columns, row))
                
                # Extraire num1 et num2 (obligatoires)
                n1 = row_dict.get('num1')
                n2 = row_dict.get('num2')
                
                if n1 is None or n2 is None:
                    continue
                    
                try:
                    n1_int = int(n1)
                    n2_int = int(n2)
                except (ValueError, TypeError):
                    continue
                    
                pair_key = tuple(sorted([n1_int, n2_int]))
                
                # Nettoyage des valeurs pour le mapping (None -> "---")
                final_attrs = {}
                for k, v in row_dict.items():
                    if k in ['num1', 'num2', 'id', 'created_at', univ_col]:
                        continue
                    final_attrs[k] = str(v) if v is not None and v != "" else "---"
                
                # Ajouter des métadonnées utiles
                final_attrs['display_value'] = row_dict.get('combination', f"{n1_int}-{n2_int}")
                
                mapping[pair_key].append(final_attrs)

            cursor.close()
            conn.close()
            return mapping
            
        except Exception as e:
            logger.error(f"Erreur loading universe map dynamique: {e}")
            return {}

    def _update_synthetic_stats(self, stats, synthetic_attrs, draw_index, draw_date):
        """Met à jour les stats pour les attributs synthétiques (moléculaires)"""
        for attr_type, attr_value in synthetic_attrs.items():
            # Les noms des types synthétiques sont déjà uniques (ex: forme_rectangle_tome_tome1)
            entry = stats[attr_type][attr_value]
            entry["count"] += 1
            entry["last_draw_index"] = draw_index
            entry["last_draw_date"] = draw_date

    def _get_geometric_zone(self, row, col):
        pass
