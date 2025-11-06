"""
Service amélioré pour exploiter la vraie structure Katula avec formes et dénominations réelles
"""
import os
import json
import psycopg2
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

load_dotenv()

class EnhancedRealKatulaService:
    def __init__(self):
        self.connection = None
        self.real_structure = None
        self.connect()
        self.load_real_structure()
    
    def connect(self):
        """Connexion à la base de données PostgreSQL"""
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
            print(f"Erreur connexion DB: {e}")
    
    def load_real_structure(self):
        """Charger la vraie structure depuis le fichier JSON"""
        try:
            structure_path = os.path.join(os.path.dirname(__file__), "..", "..", "katula_structure_reelle.json")
            with open(structure_path, 'r', encoding='utf-8') as f:
                self.real_structure = json.load(f)
        except Exception as e:
            print(f"Erreur chargement structure réelle: {e}")
            self.real_structure = {}
    
    def get_real_chip_data(self, univers: str, chip: str) -> Dict[str, Any]:
        """Récupérer les vraies données d'un chip depuis la structure réelle"""
        if not self.real_structure or univers not in self.real_structure:
            return {"error": f"Univers {univers} non trouvé dans la structure réelle"}
        
        universe_data = self.real_structure[univers]
        
        if chip not in universe_data.get("chips", {}):
            return {"error": f"Chip {chip} non trouvé dans l'univers {univers}"}
        
        chip_data = universe_data["chips"][chip]
        
        return {
            "chip": chip,
            "univers": univers,
            "nb_compartiments": chip_data["nb_compartiments"],
            "formes_reelles": chip_data["formes"],
            "petiques_reelles": chip_data["petiques"],
            "lignes": chip_data["lignes"],
            "colonnes": chip_data["colonnes"],
            "compartiments_verticaux": chip_data["compartiments_verticaux"],
            "denominations_reelles": [comp["denomination"] for comp in chip_data["compartiments_verticaux"]]
        }
    
    def get_enhanced_table_data(self, univers: str) -> Dict[str, Any]:
        """Récupérer les données de table enrichies avec la vraie structure"""
        cursor = self.connection.cursor()
        
        try:
            # Récupérer les données de la BD
            cursor.execute("""
                SELECT DISTINCT chip, ligne, colonne, forme, denomination, petique
                FROM table_de_katula 
                WHERE univers = %s 
                ORDER BY chip
            """, (univers,))
            
            db_data = cursor.fetchall()
            
            # Enrichir avec la structure réelle
            enhanced_data = []
            
            for chip, ligne, colonne, forme_db, denomination_db, petique_db in db_data:
                # Récupérer les vraies données
                real_chip_data = self.get_real_chip_data(univers, chip)
                
                if "error" not in real_chip_data:
                    enhanced_entry = {
                        "chip": chip,
                        "position": {
                            "ligne": ligne,
                            "colonne": colonne,
                            "coordonnee": f"{ligne}-{colonne}"
                        },
                        "donnees_bd": {
                            "forme": forme_db,
                            "denomination": denomination_db,
                            "petique": petique_db
                        },
                        "donnees_reelles": {
                            "formes_disponibles": real_chip_data["formes_reelles"],
                            "denominations_disponibles": real_chip_data["denominations_reelles"],
                            "petiques_disponibles": real_chip_data["petiques_reelles"],
                            "nb_compartiments": real_chip_data["nb_compartiments"],
                            "compartiments_detailles": real_chip_data["compartiments_verticaux"]
                        },
                        "mapping_status": {
                            "forme_match": forme_db in real_chip_data["formes_reelles"] if forme_db else False,
                            "denomination_match": denomination_db in real_chip_data["denominations_reelles"] if denomination_db else False,
                            "petique_match": petique_db in real_chip_data["petiques_reelles"] if petique_db else False
                        }
                    }
                else:
                    enhanced_entry = {
                        "chip": chip,
                        "position": {"ligne": ligne, "colonne": colonne},
                        "donnees_bd": {"forme": forme_db, "denomination": denomination_db, "petique": petique_db},
                        "donnees_reelles": {"error": real_chip_data["error"]},
                        "mapping_status": {"error": "Structure réelle non disponible"}
                    }
                
                enhanced_data.append(enhanced_entry)
            
            # Statistiques de mapping
            total_entries = len(enhanced_data)
            successful_mappings = len([e for e in enhanced_data if "error" not in e["donnees_reelles"]])
            
            return {
                "univers": univers,
                "total_chips": total_entries,
                "mapping_success_rate": (successful_mappings / total_entries * 100) if total_entries > 0 else 0,
                "enhanced_data": enhanced_data,
                "structure_reelle_disponible": univers in self.real_structure if self.real_structure else False,
                "formes_disponibles_univers": self.real_structure.get(univers, {}).get("formes_disponibles", []) if self.real_structure else [],
                "petiques_disponibles_univers": self.real_structure.get(univers, {}).get("petiques_disponibles", []) if self.real_structure else []
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des données: {str(e)}"}
        finally:
            cursor.close()
    
    def compare_bd_vs_real_structure(self, univers: str) -> Dict[str, Any]:
        """Comparer les données BD vs structure réelle"""
        cursor = self.connection.cursor()
        
        try:
            # Données de la BD
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT chip) as total_chips_bd,
                    COUNT(DISTINCT forme) as total_formes_bd,
                    COUNT(DISTINCT denomination) as total_denominations_bd,
                    COUNT(DISTINCT petique) as total_petiques_bd,
                    array_agg(DISTINCT forme ORDER BY forme) as formes_bd,
                    array_agg(DISTINCT petique ORDER BY petique) as petiques_bd
                FROM table_de_katula 
                WHERE univers = %s
            """, (univers,))
            
            bd_stats = cursor.fetchone()
            
            # Données de la structure réelle
            if self.real_structure and univers in self.real_structure:
                real_data = self.real_structure[univers]
                real_chips = list(real_data["chips"].keys())
                real_formes = real_data["formes_disponibles"]
                real_petiques = real_data["petiques_disponibles"]
                
                # Toutes les dénominations réelles
                real_denominations = []
                for chip_data in real_data["chips"].values():
                    for comp in chip_data["compartiments_verticaux"]:
                        if comp["denomination"] not in real_denominations:
                            real_denominations.append(comp["denomination"])
                
                comparison = {
                    "univers": univers,
                    "donnees_bd": {
                        "total_chips": bd_stats[0],
                        "total_formes": bd_stats[1],
                        "total_denominations": bd_stats[2],
                        "total_petiques": bd_stats[3],
                        "formes": bd_stats[4] if bd_stats[4] else [],
                        "petiques": bd_stats[5] if bd_stats[5] else []
                    },
                    "donnees_reelles": {
                        "total_chips": len(real_chips),
                        "total_formes": len(real_formes),
                        "total_denominations": len(real_denominations),
                        "total_petiques": len(real_petiques),
                        "formes": real_formes,
                        "petiques": real_petiques,
                        "denominations": real_denominations[:10]  # Première 10 pour l'exemple
                    },
                    "differences": {
                        "chips_manquants_bd": [chip for chip in real_chips if chip not in [f"chip{i}" for i in range(1, bd_stats[0] + 1)]],
                        "formes_manquantes_bd": [forme for forme in real_formes if forme not in (bd_stats[4] or [])],
                        "petiques_manquantes_bd": [petique for petique in real_petiques if petique not in (bd_stats[5] or [])],
                        "mapping_effectif": bd_stats[0] > 0 and len(real_chips) > 0
                    }
                }
            else:
                comparison = {
                    "univers": univers,
                    "donnees_bd": {
                        "total_chips": bd_stats[0],
                        "total_formes": bd_stats[1],
                        "formes": bd_stats[4] if bd_stats[4] else []
                    },
                    "donnees_reelles": {"error": "Structure réelle non disponible"},
                    "differences": {"error": "Impossible de comparer sans structure réelle"}
                }
            
            return comparison
            
        except Exception as e:
            return {"error": f"Erreur lors de la comparaison: {str(e)}"}
        finally:
            cursor.close()
    
    def get_refined_chip_display(self, univers: str, chip: str) -> Dict[str, Any]:
        """Affichage raffiné d'un chip avec vraies formes et dénominations"""
        real_data = self.get_real_chip_data(univers, chip)
        
        if "error" in real_data:
            return real_data
        
        # Créer un affichage raffiné
        refined_display = {
            "chip_id": chip,
            "univers": univers,
            "structure_raffinee": {
                "nb_compartiments": real_data["nb_compartiments"],
                "disposition_verticale": []
            }
        }
        
        for i, compartiment in enumerate(real_data["compartiments_verticaux"]):
            refined_compartment = {
                "position_verticale": i + 1,
                "coordonnees": f"{compartiment['ligne']}-{compartiment['colonne']}",
                "forme_geometrique": compartiment["forme"],
                "denomination_reelle": compartiment["denomination"],
                "zone_petique": compartiment["petique"],
                "attributs_visuels": {
                    "forme_description": self._get_forme_description(compartiment["forme"]),
                    "couleur_zone": self._get_zone_color(compartiment["petique"]),
                    "icone_denomination": self._get_denomination_icon(compartiment["denomination"])
                }
            }
            refined_display["structure_raffinee"]["disposition_verticale"].append(refined_compartment)
        
        return refined_display
    
    def _get_forme_description(self, forme: str) -> str:
        """Description des formes géométriques"""
        descriptions = {
            "carre": "Forme carrée - 4 côtés égaux",
            "cercle": "Forme circulaire - courbe fermée",
            "rectangle": "Forme rectangulaire - 4 côtés, angles droits",
            "triangle": "Forme triangulaire - 3 côtés"
        }
        return descriptions.get(forme, f"Forme: {forme}")
    
    def _get_zone_color(self, petique: str) -> str:
        """Couleurs associées aux zones pétiques"""
        colors = {
            "q1": "#FF6B6B",  # Rouge
            "q2": "#4ECDC4",  # Turquoise
            "q3": "#45B7D1",  # Bleu
            "q4": "#96CEB4"   # Vert
        }
        return colors.get(petique, "#CCCCCC")
    
    def _get_denomination_icon(self, denomination: str) -> str:
        """Icônes pour les dénominations"""
        icons = {
            "road": "🛣️", "bike": "🚲", "chair": "🪑", "table": "🪑",
            "window": "🪟", "door": "🚪", "forest": "🌲", "mountain": "⛰️",
            "shoes": "👟", "gold": "🏆", "book": "📚", "fish": "🐟",
            "flower": "🌸", "hotel": "🏨", "rope": "🪢", "spoon": "🥄",
            "scissors": "✂️", "football": "⚽", "fire": "🔥"
        }
        
        # Extraire le mot clé de la dénomination
        for key in icons:
            if key in denomination.lower():
                return icons[key]
        
        return "📍"  # Icône par défaut

# Instance globale
enhanced_real_katula_service = EnhancedRealKatulaService()