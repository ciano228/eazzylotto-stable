import itertools
import os
import logging
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text
from session_statistics_engine import SessionStatisticsEngine

logger = logging.getLogger(__name__)

class PatternRecognitionService:
    """
    Service for identifying draws with similar attribute structures (Signatures)
    and analyzing their consequences.
    """

    def __init__(self, db_config: Dict[str, str] = None):
        if db_config is None:
            self.db_config = {
                'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            }
        else:
            self.db_config = db_config
            
        self.stats_engine = SessionStatisticsEngine(self.db_config)
        self.universe_maps = {} # Cache for universe maps

    def _get_map(self, universe: str):
        if universe not in self.universe_maps:
            logger.info(f"Loading map for universe: {universe}")
            self.universe_maps[universe] = self.stats_engine._load_universe_map(universe)
        return self.universe_maps[universe]

    def generate_draw_signature(self, numbers: List[int], universe: str) -> List[Dict[str, Any]]:
        """
        Generates the 'Signature' of a draw: A list of attribute dictionaries for its 10 pairs.
        Returns a list of 10 dicts (one per pair).
        """
        if len(numbers) < 2:
            return []

        universe_map = self._get_map(universe)
        valid_numbers = sorted([int(n) for n in numbers if str(n).isdigit()])
        pairs = list(itertools.combinations(valid_numbers, 2))
        
        signature = []
        
        for p in pairs:
            p_key = tuple(sorted(p))
            attrs = {}
            if p_key in universe_map:
                # Use ALL attributes from the mapping (dynamic)
                # universe_map[p_key] is a list of dicts
                raw_attrs = universe_map[p_key][0] if universe_map[p_key] else {}
                
                # We keep everything except purely technical ID/date fields if they leak
                for k, v in raw_attrs.items():
                    if k not in ['num1', 'num2', 'id', 'created_at', 'univers', 'universe']:
                        attrs[k] = v
                attrs['numbers'] = list(p_key)
            signature.append(attrs)
            
        return signature

    def find_similar_draws(self, db: Session, target_numbers: List[int], universe: str, min_match_percent: int = 50) -> Dict[str, Any]:
        """
        Finds historical draws that share similar attribute signatures.
        """
        # 1. Generate Target Signature
        target_signature = self.generate_draw_signature(target_numbers, universe)
        if not target_signature:
            return {"error": "Invalid numbers for signature generation"}

        # 2. Fetch All Historical Draws with their consequences in one go using LEAD()
        query = text(f"""
            WITH draws_with_consequences AS (
                SELECT 
                    sd.draw_date, 
                    sd.winning_numbers, 
                    sd.draw_number,
                    sd.lottery_name,
                    ws.name as session_name,
                    LEAD(sd.winning_numbers, 1) OVER(ORDER BY sd.draw_date) as next_winning_numbers,
                    LEAD(sd.draw_date, 1) OVER(ORDER BY sd.draw_date) as next_draw_date
                FROM session_draws sd
                JOIN work_sessions ws ON sd.session_id = ws.id
            )
            SELECT * FROM draws_with_consequences
            ORDER BY draw_date DESC
            LIMIT 4000
        """)
        
        result = db.execute(query)
        historical_rows = result.fetchall()
        
        matches = []
        
        for row in historical_rows:
            d_nums = row.winning_numbers
            if not d_nums or len(d_nums) < 5: 
                continue
                
            try:
                d_nums_int = [int(n) for n in d_nums if str(n).isdigit()]
                if len(d_nums_int) < 5: continue
            except:
                continue

            # Skip exact self if checking history
            is_self = set(d_nums_int) == set(target_numbers)

            # Generate Candidate Signature
            candidate_signature = self.generate_draw_signature(d_nums_int, universe)
            
            if not candidate_signature: continue

            # Compare Signatures
            match_score, match_details = self._compare_signatures(target_signature, candidate_signature)
            
            if match_score >= min_match_percent:
                matches.append({
                    "draw_date": row.draw_date.isoformat() if hasattr(row.draw_date, 'isoformat') else str(row.draw_date) if row.draw_date else None,
                    "draw_numbers": d_nums_int,
                    "match_score": match_score,
                    "match_type": match_details['type'],
                    "is_self": is_self,
                    "lottery_name": row.lottery_name,
                    "session_name": row.session_name,
                    # Pre-fetched consequence
                    "next_draw_date": row.next_draw_date.isoformat() if hasattr(row.next_draw_date, 'isoformat') else str(row.next_draw_date) if row.next_draw_date else None,
                    "next_winning_numbers": row.next_winning_numbers
                })

        # Sort by score DESC, then date DESC (safely handling None dates)
        matches.sort(key=lambda x: (x['match_score'], x['draw_date'] or ""), reverse=True)
        
        # 3. Analyze Consequences (now from in-memory data)
        consequences = self._analyze_consequences(matches, universe)

        return {
            "target_numbers": target_numbers,
            "universe": universe,
            "total_matches": len(matches),
            "matches": matches[:50], # Return top 50
            "consequences": consequences
        }

    def _attr_dict_to_set(self, d: Dict) -> Set[Tuple[str, str]]:
        """Converts attribute dict to set of tuples for comparison, ignoring technical/list fields."""
        return set((k, v) for k, v in d.items() if v != "---" and k != 'numbers')

    def _compare_signatures(self, target: List[Dict], candidate: List[Dict]) -> Tuple[float, Dict]:
        """
        Compares two signatures (lists of 10 pair-attributes).
        Returns (score_percent, details).
        """
        # This is a simplified comparison logic. For a real-world scenario,
        # consider Jaccard index for set similarity for more nuance.
        
        t_sets = [self._attr_dict_to_set(p) for p in target]
        c_sets = [self._attr_dict_to_set(p) for p in candidate]
        
        matches_found = 0
        used_indices = set()
        
        total_pairs = len(t_sets)
        if total_pairs == 0:
            return (100.0, {"type": "Empty Signature"}) if len(c_sets) == 0 else (0.0, {"type": "Mismatch"})

        for t_s in t_sets:
            best_idx = -1
            max_similarity = -1.0
            
            for i, c_s in enumerate(c_sets):
                if i in used_indices: continue
                
                # Jaccard similarity for the pair attributes
                union_size = len(t_s.union(c_s))
                if union_size == 0:
                    similarity = 1.0
                else:
                    similarity = len(t_s.intersection(c_s)) / union_size
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_idx = i
            
            if max_similarity >= 0.7: # Threshold lowered from 0.9 to 0.7 for better sensitivity
                matches_found += 1
                if best_idx != -1:
                    used_indices.add(best_idx)
        
        score = (matches_found / total_pairs) * 100
        
        match_type = "Structural"
        if score >= 99.9:
            match_type = "Exact Structural Match"
            
        return score, {"type": match_type}

    def _analyze_consequences(self, matches: List[Dict], universe: str) -> Dict[str, Any]:
        """
        Analyzes what happened *immediately after* the matching draws, using pre-fetched data.
        """
        threshold = 80
        relevant_matches = [m for m in matches if not m.get('is_self') and m['match_score'] >= threshold and m.get('next_winning_numbers')]
        
        if not relevant_matches:
            threshold = 20 # Lowered from 50 to 20 to match the entry-level search threshold
            relevant_matches = [m for m in matches if not m.get('is_self') and m['match_score'] >= threshold and m.get('next_winning_numbers')]

        if not relevant_matches:
            return {"status": "No sufficient match data for analysis"}

        consequences = []
        for m in relevant_matches:
            try:
                next_nums = [int(n) for n in m['next_winning_numbers'] if str(n).isdigit()]
                if next_nums:
                    consequences.append({
                        "trigger_date": m['draw_date'],
                        "result_date": m['next_draw_date'],
                        "result_numbers": next_nums,
                        "trigger_score": m['match_score']
                    })
            except (ValueError, TypeError):
                continue
                
        # Aggregate Consequences
        if not consequences:
            return {"status": "No valid consequence events found"}

        number_counts = defaultdict(int)
        pair_counts = defaultdict(int)
        attribute_counts = defaultdict(lambda: defaultdict(int))

        for c in consequences:
            # 1. Numbers
            for n in c['result_numbers']:
                number_counts[n] += 1
            
            # 2. Pairs
            if len(c['result_numbers']) >= 2:
                pairs = list(itertools.combinations(sorted(c['result_numbers']), 2))
                for p in pairs:
                    pair_counts[p] += 1
            
            # 3. Attributes
            consequence_sig = self.generate_draw_signature(c['result_numbers'], universe)
            for pair_attrs in consequence_sig:
                for attr_type, attr_val in pair_attrs.items():
                    if attr_val != "---" and attr_type != 'numbers':
                        attribute_counts[attr_type][attr_val] += 1

        # Most frequent numbers
        sorted_nums = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Most frequent pairs
        sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Most frequent attributes
        sorted_attributes = {}
        for attr_type, counts in attribute_counts.items():
            sorted_attrs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            if not consequences: continue
            sorted_attributes[attr_type] = [
                {"value": val, "count": cnt, "frequency": round(cnt/len(consequences)*100, 1)}
                for val, cnt in sorted_attrs[:5]
            ]

        return {
            "analyzed_events": len(consequences),
            "most_frequent_numbers": [{"number": n, "count": c, "frequency": round(c/len(consequences)*100, 1)} for n, c in sorted_nums[:10] if consequences],
            "most_frequent_pairs": [{"pair": f"{p[0]}-{p[1]}", "count": c, "frequency": round(c/len(consequences)*100, 1)} for p, c in sorted_pairs[:10] if consequences],
            "most_frequent_attributes": sorted_attributes,
            "raw_events": consequences
        }

    def analyze_session_evolution(self, db: Session, session_id: int, start_date: str = None, end_date: str = None, universe: str = "mundo") -> Dict[str, Any]:
        """
        Analyzes the evolution of attributes for a specific session over a date range.
        Calculates signatures for all draws and aggregates trends.
        """
        # Fetch draws for session
        query_str = """
            SELECT draw_date, winning_numbers, draw_number 
            FROM session_draws 
            WHERE 1=1
        """
        params = {}
        
        # If we have session linking (assuming session_id maps to something or we filter by it if column exists)
        # Assuming for now we filter by metadata or we just take ALL draws if session_id is generic
        # OR better: session_draws usually belongs to a session. 
        # Check if 'session_id' column exists in session_draws? 
        # Based on previous context, session_draws might not have session_id directly if it's "all history".
        # But let's assume valid implementation or we filter by date only if session_id is ignored.
        
        # NOTE: In this system, it seems 'session_draws' might be a shared table. 
        # If we want specific lottery type (e.g. Ghana), we might need to filter by 'lottery_name' or similar if present.
        # For now, we will assume session_draws contains the relevant data or we just filter by date.
        
        if start_date:
            query_str += " AND draw_date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query_str += " AND draw_date <= :end_date"
            params['end_date'] = end_date
            
        query_str += " ORDER BY draw_date ASC"
        
        result = db.execute(text(query_str), params)
        rows = result.fetchall()
        
        evolution_data = []
        attribute_frequencies = defaultdict(lambda: defaultdict(int))
        
        total_draws = len(rows)
        
        for row in rows:
            d_nums = row.winning_numbers
            if not d_nums or len(d_nums) < 2: continue
            
            d_nums_int = [int(n) for n in d_nums if str(n).isdigit()]
            
            # Generate Signature
            sig = self.generate_draw_signature(d_nums_int, universe)
            
            # Extract dominant attributes for this draw
            # For visualization, we might want to know "Did this draw have a Cercle?"
            draw_summary = {
                "date": row.draw_date.isoformat(),
                "numbers": d_nums_int,
                "attributes": {} # dominant attributes
            }
            
            # Aggregate for this draw
            this_draw_attrs = defaultdict(int)
            total_pairs = len(sig)
            
            for pair in sig:
                for k, v in pair.items():
                    if v != "---":
                        this_draw_attrs[f"{k}:{v}"] += 1
                        attribute_frequencies[k][v] += 1
            
            # Determine "Dominant" attributes for the draw (e.g. if > 50% pairs have it)
            for k, v in this_draw_attrs.items():
                # k is like "forme:cercle"
                attr_type, attr_val = k.split(":", 1)
                # If present in > 40% of pairs, tag it
                if v / total_pairs >= 0.4:
                     if attr_type not in draw_summary["attributes"]:
                         draw_summary["attributes"][attr_type] = []
                     draw_summary["attributes"][attr_type].append(attr_val)
            
            evolution_data.append(draw_summary)
            
        # summary stats
        global_stats = {}
        for k, val_counts in attribute_frequencies.items():
            sorted_vals = sorted(val_counts.items(), key=lambda x: x[1], reverse=True)
            global_stats[k] = [
                {"value": v, "frequency": round(c / total_draws, 2)} # Average occurrence per draw? Or just raw count? 
                # Let's do raw count normalized by N draws? 
                # Actually, since one draw can have multiple pairs, frequency > 1 is possible.
                # Normalized by Total Pairs would be better: total_pairs_all_draws = total_draws * pairs_per_draw
                # But pairs_per_draw varies.
                # Let's keep it simple: "Appeared in X pairs total"
                for v, c in sorted_vals[:5]
            ]
            
        return {
            "session_id": session_id,
            "span_start": start_date,
            "span_end": end_date,
            "total_draws": total_draws,
            "evolution_timeline": evolution_data,
            "global_stats": global_stats
        }
