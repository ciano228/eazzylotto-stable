import re
from typing import Dict, Any, List, Tuple, Optional

class QueryBuilderService:
    """
    Neuro-Katula Engine: Natural Language to Query (NL2Q)
    Translates user questions into structured SQL filters for the 'combinations' table.
    """

    def __init__(self):
        # 1. Knowledge Graph (Mappings)
        self.column_map = {
            "numero": ["num1", "num2"],
            "chiffre": ["num1", "num2"],
            "combinaison": "combination",
            "forme": "forme",
            "tome": "tome",
            "ligne": "ligne", 
            "colonne": "colonne",
            "beastie": "beastie",
            "univers": "univers",
            "puce": "chip", "chip": "chip"
        }

        # 2. Known Values (The Neural Dictionary)
        # Fetched from DB analysis
        self.known_values = {
            "beastie": [
                'cat', 'cock', 'cow', 'crocodile', 'dog', 'eagle', 
                'elephant', 'goat', 'horse', 'lion', 'scorpion', 
                'tiger', 'tortoise', 'viper', 'zebra'
            ],
            "univers": [
                'fruity', 'mundo', 'roaster', 'sunshine', 'trigga'
            ],
            "forme": ['triangle', 'carre', 'cercle', 'rectangle']
        }
        
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point.
        Returns a dictionary representing the query intent and filters.
        """
        normalized_query = user_query.lower()
        filters = {}

        # --- STRATEGY: Keyword Scanning (Robust) ---
        # Scan for known values from our dictionary
        
        # 1. Beasties & Universes & Formes
        for category, values in self.known_values.items():
            for val in values:
                # Check for singular AND plural (basic s check)
                # We use word boundaries \b to avoid matching "cat" in "category"
                pattern = r"\b" + re.escape(val) + r"s?\b"
                if re.search(pattern, normalized_query):
                    filters[category] = val

        # --- STRATEGY: Pattern Extraction (Specifics) ---

        # 2. Tome (Tome 1, Tome 2...)
        tome_match = re.search(r"tome\s?(\d+)", normalized_query)
        if tome_match:
            filters["tome"] = f"tome{tome_match.group(1)}"

        # 3. Ligne / Colonne (Ligne 1, Col 2)
        line_match = re.search(r"lignes?\s?(\d+)", normalized_query)
        if line_match:
            filters["ligne"] = f"L{line_match.group(1)}"
            
        col_match = re.search(r"col(:?onnes?)?\s?(\d+)", normalized_query)
        if col_match:
            filters["colonne"] = f"C{col_match.group(1)}"

        # 4. Chips (Puce 12, Chip 5)
        # Handle 'puce 12', 'chip 12', or just 'chip12'
        chip_match = re.search(r"(?:puce|chip)\s?(\d+)", normalized_query)
        if chip_match:
            filters["chip"] = f"chip{chip_match.group(1)}"

        # 5. Period (Période 5, P5)
        period_match = re.search(r"p[ée]riodes?\s?(\d+)", normalized_query)
        if period_match:
            filters["period"] = int(period_match.group(1))

        # 6. Numeric Values (Detecting =0, à 0, est null, vide, etc.)
        value_match = re.search(r"(?:=|à|est\s?à|est\s?|renvoie\s?|retourne\s?|rend\s?|donne\s?)\s?(\d+|null|vide|rien)", normalized_query)
        if value_match:
            raw_val = value_match.group(1)
            if raw_val in ["null", "vide", "rien"]:
                filters["target_value"] = 0
            else:
                filters["target_value"] = int(raw_val)

        # --- INTENT DETECTION ---
        intent = "EXPLORE"
        if any(w in normalized_query for w in ["régulier", "regular", "stable", "fixe"]):
            intent = "ANALYZE_REGULARITY"
        elif any(w in normalized_query for w in ["aucun", "pas de", "manque", "vide", "n'affiche pas", "est null"]):
            intent = "FIND_MISSING"
        elif any(w in normalized_query for w in ["affiche", "montre", "quel", "quelle", "où", "trouve", "renvoie", "retourne", "rend", "donne"]):
            # If we have a target value like 0, it might be FIND_OCCURRENCE
            if filters.get("target_value") is not None:
                intent = "FIND_OCCURRENCE"
            else:
                intent = "EXPLORE"

        return {
            "intent": intent,
            "filters": filters,
            "sql_clause": self._build_sql_clause(filters),
            "original_query": user_query
        }

    def _build_sql_clause(self, filters: Dict[str, str]) -> str:
        """
        Converts filters dict to SQL WHERE clause using named placeholders.
        Safe: Uses :key format for SQLAlchemy text().
        """
        if not filters:
            return "1=1"

        clauses = []
        for col in filters.keys():
            # Basic validation to prevent injection in column names
            if not re.match(r"^[a-zA-Z0-9_]+$", col):
                continue
            
            clauses.append(f"{col} = :{col}")

        return " AND ".join(clauses)
