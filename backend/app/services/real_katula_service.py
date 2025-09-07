"""
Service pour exploiter la structure réelle des tables Katula
Colonnes: chip_id, univers, ligne, colonne, petique, chip, forme, denomination
"""
import os
import psycopg2
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class RealKatulaService:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connexion à la base de données"""
        try:
            DATABASE_URL = os.getenv("DATABASE_URL")
            parts = DATABASE_URL.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            host_port = host_db[0].split(":")
            
            self.connection = psycopg2.connect(
                host=host_port[0],
                port=host_port[1] if len(host_port) > 1 else "5432",
                database=host_db[1],
                user=user_pass[0],
                password=user_pass[1]
            )
        except Exception as e:
            print(f"Erreur connexion: {e}")
    
    def get_univers_list(self) -> List[str]:
        """Récupérer la liste des univers disponibles"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
        return [u[0] for u in cursor.fetchall()]
    
    def get_formes_by_univers(self, univers: str) -> List[str]:
        """Récupérer les formes disponibles pour un univers"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT forme 
            FROM table_de_katula 
            WHERE univers = %s AND forme IS NOT NULL
            ORDER BY forme
        """, (univers,))
        return [f[0] for f in cursor.fetchall()]
    
    def get_chips_by_univers(self, univers: str) -> List[str]:
        """Récupérer les chips disponibles pour un univers"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT chip 
            FROM table_de_katula 
            WHERE univers = %s AND chip IS NOT NULL
            ORDER BY chip
        """, (univers,))
        return [c[0] for c in cursor.fetchall()]
    
    def get_chip_vertical_layout(self, univers: str, chip: str) -> List[Dict]:
        """Récupérer la disposition verticale d'un chip (4 cellules pour Mundo)"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT ligne, colonne, forme, petique, denomination
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
            ORDER BY ligne, colonne
        """, (univers, chip))
        
        layout = []
        for i, (ligne, colonne, forme, petique, denomination) in enumerate(cursor.fetchall()):
            layout.append({
                'position_verticale': i + 1,
                'ligne': ligne,
                'colonne': colonne,
                'forme': forme,
                'petique': petique,
                'denomination': denomination,
                'coordonnee': f"{ligne}-{colonne}"
            })
        
        return layout
    
    def get_chip_structure_complete(self, univers: str, chip: str) -> Dict:
        """Récupérer la structure complète d'un chip avec ses compartiments"""
        cursor = self.connection.cursor()
        
        # Informations générales
        cursor.execute("""
            SELECT COUNT(*) as nb_compartiments
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
        """, (univers, chip))
        
        nb_comp = cursor.fetchone()[0]
        
        # Disposition verticale
        layout = self.get_chip_vertical_layout(univers, chip)
        
        # Formes et petiques utilisées
        cursor.execute("""
            SELECT 
                array_agg(DISTINCT forme ORDER BY forme) as formes,
                array_agg(DISTINCT petique ORDER BY petique) as petiques,
                array_agg(DISTINCT ligne ORDER BY ligne) as lignes,
                array_agg(DISTINCT colonne ORDER BY colonne) as colonnes
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
        """, (univers, chip))
        
        result = cursor.fetchone()
        formes, petiques, lignes, colonnes = result
        
        return {
            'chip': chip,
            'univers': univers,
            'nb_compartiments': nb_comp,
            'formes_utilisees': formes,
            'petiques_utilisees': petiques,
            'lignes_utilisees': lignes,
            'colonnes_utilisees': colonnes,
            'disposition_verticale': layout
        }
    
    def get_all_chips_by_univers(self, univers: str) -> List[Dict]:
        """Récupérer tous les chips d'un univers avec leur structure"""
        chips = self.get_chips_by_univers(univers)
        result = []
        
        for chip in chips:
            structure = self.get_chip_structure_complete(univers, chip)
            result.append(structure)
        
        return result
    
    def get_formes_compartiments(self, univers: str) -> Dict:
        """Récupérer la répartition des formes par compartiments"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT forme, COUNT(*) as count
            FROM table_de_katula 
            WHERE univers = %s AND forme IS NOT NULL
            GROUP BY forme
            ORDER BY count DESC
        """, (univers,))
        
        formes_stats = {}
        for forme, count in cursor.fetchall():
            formes_stats[forme] = count
        
        return formes_stats
    
    def search_by_forme(self, univers: str, forme: str) -> List[Dict]:
        """Rechercher tous les chips contenant une forme spécifique"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT chip, ligne, colonne, petique, denomination
            FROM table_de_katula 
            WHERE univers = %s AND forme = %s
            ORDER BY chip, ligne, colonne
        """, (univers, forme))
        
        results = []
        for chip, ligne, colonne, petique, denomination in cursor.fetchall():
            results.append({
                'chip': chip,
                'ligne': ligne,
                'colonne': colonne,
                'petique': petique,
                'denomination': denomination,
                'coordonnee': f"{ligne}-{colonne}"
            })
        
        return results

# Instance globale
real_katula_service = RealKatulaService()
