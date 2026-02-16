"""
Synthetic Attribute Engine
Génère des attributs composites (moléculaires) à partir d'attributs atomiques
"""

import json
import os
from typing import Dict, List, Any

class SyntheticAttributeEngine:
    def __init__(self, recipes_path=None):
        self.recipes = []
        if recipes_path and os.path.exists(recipes_path):
            self.load_recipes(recipes_path)
        else:
            # Fallback local if integrated
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_recipes = os.path.join(base_dir, '..', 'synthetic_recipes.json')
            if os.path.exists(local_recipes):
                self.load_recipes(local_recipes)

    def load_recipes(self, path: str):
        """Charge les recettes depuis un fichier JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.recipes = json.load(f)
            print(f"SyntheticAttributeEngine: {len(self.recipes)} recettes chargées.")
        except Exception as e:
            print(f"Erreur chargement recettes: {e}")

    def synthesize(self, atomic_attrs: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère des attributs synthétiques à partir d'un dictionnaire d'attributs atomiques.
        
        Input: {'forme': 'rectangle', 'tome': 'tome1', ...}
        Output: {'forme_rectangle_tome_tome1': 'rectangle_tome1', ...}
        """
        synthetic_attrs = {}
        
        for recipe in self.recipes:
            # Vérifier si tous les composants requis sont présents
            missing = False
            for comp in recipe['components']:
                if comp not in atomic_attrs or atomic_attrs[comp] is None:
                    missing = True
                    break
            
            if missing:
                continue
                
            # Appliquer la formule de concaténation
            # La formule est du type "{forme}_{tome}"
            try:
                # On formate la chaîne en utilisant les valeurs des attributs atomiques
                value = recipe['formula'].format(**atomic_attrs)
                synthetic_attrs[recipe['name']] = value
            except KeyError as e:
                # Au cas où un attribut manque malgré le check
                continue
                
        return synthetic_attrs

    def get_available_synthetic_types(self) -> List[str]:
        """Retourne la liste des types d'attributs synthétiques disponibles"""
        return [r['name'] for r in self.recipes]
