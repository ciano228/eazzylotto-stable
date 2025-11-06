"""
Service de mapping entre la base de données et l'interface utilisateur Katula
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class KatulaUIElement:
    """Représentation d'un élément UI de Katula"""
    type: str  # 'chip', 'forme', 'compartiment', 'quadrant'
    position: Dict[str, Any]  # Position dans l'UI
    style: Dict[str, str]  # Styles CSS
    content: Any  # Contenu de l'élément
    metadata: Dict[str, Any]  # Métadonnées supplémentaires

class KatulaUIMapper:
    """Service de mapping entre la BD et l'UI"""
    
    def __init__(self):
        # Mapping des formes vers leurs icônes
        self.forme_icons = {
            'carre': '⬛',
            'triangle': '△',
            'cercle': '○',
            'rectangle': '▭',
            'carre-triangle': '⬛△',
            'carre-cercle': '⬛○',
            'carre-rectangle': '⬛▭',
            'triangle-carre': '△⬛',
            'triangle-cercle': '△○',
            'triangle-rectangle': '△▭',
            'cercle-carre': '○⬛',
            'cercle-triangle': '○△',
            'cercle-rectangle': '○▭',
            'rectangle-carre': '▭⬛',
            'rectangle-triangle': '▭△',
            'rectangle-cercle': '▭○'
        }
        
        # Mapping des positions des quadrants
        self.quadrant_positions = {
            'Q1': {'start_row': 1, 'end_row': 4, 'start_col': 1, 'end_col': 3},
            'Q2': {'start_row': 1, 'end_row': 4, 'start_col': 4, 'end_col': 6},
            'Q3': {'start_row': 5, 'end_row': 8, 'start_col': 1, 'end_col': 3},
            'Q4': {'start_row': 5, 'end_row': 8, 'start_col': 4, 'end_col': 6}
        }
        
        # Styles par type d'élément
        self.element_styles = {
            'chip': {
                'background': 'white',
                'border': '1px solid #ddd',
                'border-radius': '8px',
                'padding': '10px',
                'min-height': '120px'
            },
            'forme': {
                'font-size': '24px',
                'color': '#2c3e50',
                'margin-bottom': '5px'
            },
            'compartiment': {
                'padding': '5px',
                'margin': '2px',
                'border-radius': '4px',
                'background': '#f8f9fa'
            },
            'denomination': {
                'font-size': '14px',
                'color': '#666',
                'margin-left': '5px'
            }
        }
    
    def map_db_to_ui(self, db_data: Dict[str, Any]) -> KatulaUIElement:
        """Convertit les données de la BD en élément UI"""
        element_type = self._determine_element_type(db_data)
        position = self._calculate_position(db_data)
        style = self.element_styles.get(element_type, {})
        content = self._format_content(db_data)
        metadata = self._extract_metadata(db_data)
        
        return KatulaUIElement(
            type=element_type,
            position=position,
            style=style,
            content=content,
            metadata=metadata
        )
    
    def _determine_element_type(self, db_data: Dict[str, Any]) -> str:
        """Détermine le type d'élément UI basé sur les données de la BD"""
        if 'chip_id' in db_data:
            return 'chip'
        elif 'forme' in db_data:
            return 'forme'
        elif 'denomination' in db_data:
            return 'compartiment'
        else:
            return 'unknown'
    
    def _calculate_position(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule la position dans l'UI basée sur les données de la BD"""
        position = {}
        
        if 'ligne' in db_data and 'colonne' in db_data:
            ligne = int(db_data['ligne'].replace('L', ''))
            colonne = int(db_data['colonne'].replace('C', ''))
            
            position.update({
                'row': ligne,
                'col': colonne,
                'quadrant': self._get_quadrant(ligne, colonne)
            })
        
        return position
    
    def _format_content(self, db_data: Dict[str, Any]) -> Any:
        """Formate le contenu pour l'affichage UI"""
        if 'forme' in db_data:
            return {
                'icon': self.forme_icons.get(db_data['forme'], '?'),
                'text': db_data['forme']
            }
        elif 'denomination' in db_data:
            denominations = db_data['denomination'].split('/')
            return {
                'denominations': denominations,
                'petique': db_data.get('petique', '').lower()
            }
        
        return db_data
    
    def _extract_metadata(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les métadonnées supplémentaires pour l'UI"""
        return {
            'univers': db_data.get('univers'),
            'petique': db_data.get('petique', '').lower(),
            'chip_id': db_data.get('chip_id'),
            'quadrant': self._get_quadrant(
                int(db_data.get('ligne', '0').replace('L', '')),
                int(db_data.get('colonne', '0').replace('C', ''))
            )
        }
    
    def _get_quadrant(self, ligne: int, colonne: int) -> str:
        """Détermine le quadrant basé sur la position"""
        if ligne <= 4:
            return 'Q1' if colonne <= 3 else 'Q2'
        else:
            return 'Q3' if colonne <= 3 else 'Q4'