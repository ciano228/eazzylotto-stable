"""
Service pour adapter la disposition des tables Katula selon la structure BD
"""
from typing import Dict, List, Any
import json

class KatulaLayoutService:
    """Service pour gérer la disposition conforme à la BD"""
    
    def __init__(self):
        self.structure_path = "katula_structure_reelle.json"
        
    def get_table_layout(self, universe: str) -> Dict[str, Any]:
        """Génère la disposition de table pour un univers donné"""
        try:
            with open(self.structure_path, 'r', encoding='utf-8') as f:
                structure = json.load(f)
        except FileNotFoundError:
            return self._get_default_layout(universe)
            
        if universe not in structure:
            return self._get_default_layout(universe)
            
        universe_data = structure[universe]
        return self._build_layout_from_structure(universe_data)
    
    def _build_layout_from_structure(self, universe_data: Dict) -> Dict[str, Any]:
        """Construit la disposition à partir de la structure"""
        layout = {
            "grid": {},
            "formes": universe_data.get("formes_disponibles", []),
            "petiques": universe_data.get("petiques_disponibles", []),
            "chips": {}
        }
        
        # Organiser par lignes et colonnes
        for chip_name, chip_data in universe_data.get("chips", {}).items():
            chip_num = chip_name.replace("chip", "")
            
            for compartiment in chip_data.get("compartiments_verticaux", []):
                ligne = compartiment["ligne"]
                colonne = compartiment["colonne"]
                
                if ligne not in layout["grid"]:
                    layout["grid"][ligne] = {}
                    
                if colonne not in layout["grid"][ligne]:
                    layout["grid"][ligne][colonne] = []
                    
                layout["grid"][ligne][colonne].append({
                    "chip": chip_num,
                    "forme": compartiment["forme"],
                    "petique": compartiment["petique"],
                    "denomination": compartiment["denomination"]
                })
                
        return layout
    
    def _get_default_layout(self, universe: str) -> Dict[str, Any]:
        """Layout par défaut si structure non trouvée"""
        return {
            "grid": {
                "L1": {
                    "C1": [{"chip": "1", "forme": "carre", "petique": "q1", "denomination": "default"}]
                }
            },
            "formes": ["carre"],
            "petiques": ["q1"],
            "chips": {}
        }
    
    def format_for_frontend(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """Formate la disposition pour le frontend"""
        return {
            "tableStructure": layout["grid"],
            "availableFormes": layout["formes"],
            "availablePetiques": layout["petiques"],
            "totalChips": len(layout.get("chips", {}))
        }
    
    def get_chip_details(self, universe: str, chip_id: str) -> Dict[str, Any]:
        """Récupère les détails d'un chip spécifique"""
        try:
            with open(self.structure_path, 'r', encoding='utf-8') as f:
                structure = json.load(f)
        except FileNotFoundError:
            return {}
            
        if universe not in structure:
            return {}
            
        chip_key = f"chip{chip_id}"
        return structure[universe].get("chips", {}).get(chip_key, {})