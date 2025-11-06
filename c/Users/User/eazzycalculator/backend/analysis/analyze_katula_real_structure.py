#!/usr/bin/env python3
"""
Analyse de la vraie structure Katula avec les bonnes colonnes
"""
import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()

def analyze_real_katula_structure():
    """Analyser la structure réelle des compartiments Katula"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        
        cursor = conn.cursor()
        
        print("=== ANALYSE STRUCTURE KATULA REELLE ===\n")
        
        # 1. Structure générale par univers
        cursor.execute("""
            SELECT 
                univers,
                COUNT(*) as total_entries,
                COUNT(DISTINCT chip) as unique_chips,
                COUNT(DISTINCT forme) as unique_formes,
                COUNT(DISTINCT petique) as unique_petiques,
                COUNT(DISTINCT ligne) as unique_lignes,
                COUNT(DISTINCT colonne) as unique_colonnes
            FROM table_de_katula 
            WHERE univers IS NOT NULL
            GROUP BY univers 
            ORDER BY univers
        """)
        
        universes_stats = cursor.fetchall()
        
        print("STATISTIQUES PAR UNIVERS:")
        for univers, total, chips, formes, petiques, lignes, colonnes in universes_stats:
            print(f"  {univers.upper()}:")
            print(f"    - Total entrées: {total}")
            print(f"    - Chips uniques: {chips}")
            print(f"    - Formes uniques: {formes}")
            print(f"    - Petiques uniques: {petiques}")
            print(f"    - Lignes uniques: {lignes}")
            print(f"    - Colonnes uniques: {colonnes}")
        
        # 2. Structure détaillée par univers
        structure_complete = {}
        
        for univers, _, _, _, _, _, _ in universes_stats:
            print(f"\n=== UNIVERS {univers.upper()} ===")
            
            # Toutes les formes disponibles
            cursor.execute("""
                SELECT DISTINCT forme 
                FROM table_de_katula 
                WHERE univers = %s AND forme IS NOT NULL
                ORDER BY forme
            """, (univers,))
            formes = [f[0] for f in cursor.fetchall()]
            print(f"Formes disponibles: {formes}")
            
            # Toutes les petiques disponibles
            cursor.execute("""
                SELECT DISTINCT petique 
                FROM table_de_katula 
                WHERE univers = %s AND petique IS NOT NULL
                ORDER BY petique
            """, (univers,))
            petiques = [p[0] for p in cursor.fetchall()]
            print(f"Petiques disponibles: {petiques}")
            
            # Structure par chip (disposition verticale)
            cursor.execute("""
                SELECT 
                    chip,
                    COUNT(*) as nb_compartiments,
                    array_agg(DISTINCT forme ORDER BY forme) as formes_chip,
                    array_agg(DISTINCT petique ORDER BY petique) as petiques_chip,
                    array_agg(DISTINCT ligne ORDER BY ligne) as lignes_chip,
                    array_agg(DISTINCT colonne ORDER BY colonne) as colonnes_chip
                FROM table_de_katula 
                WHERE univers = %s 
                GROUP BY chip 
                ORDER BY chip
                LIMIT 10
            """, (univers,))
            
            chips_structure = cursor.fetchall()
            
            structure_univers = {
                'formes_disponibles': formes,
                'petiques_disponibles': petiques,
                'chips': {}
            }
            
            print(f"Structure des premiers chips:")
            for chip, nb_comp, formes_chip, petiques_chip, lignes_chip, colonnes_chip in chips_structure:
                print(f"  {chip}: {nb_comp} compartiments")
                print(f"    Formes: {formes_chip}")
                print(f"    Petiques: {petiques_chip}")
                print(f"    Lignes: {lignes_chip}")
                print(f"    Colonnes: {colonnes_chip}")
                
                # Détail des compartiments pour ce chip (disposition verticale)
                cursor.execute("""
                    SELECT ligne, colonne, forme, petique, denomination
                    FROM table_de_katula 
                    WHERE univers = %s AND chip = %s
                    ORDER BY ligne, colonne
                """, (univers, chip))
                
                compartiments = cursor.fetchall()
                
                structure_chip = {
                    'nb_compartiments': nb_comp,
                    'formes': formes_chip,
                    'petiques': petiques_chip,
                    'lignes': lignes_chip,
                    'colonnes': colonnes_chip,
                    'compartiments_verticaux': []
                }
                
                for ligne, colonne, forme, petique, denomination in compartiments:
                    structure_chip['compartiments_verticaux'].append({
                        'ligne': ligne,
                        'colonne': colonne,
                        'forme': forme,
                        'petique': petique,
                        'denomination': denomination
                    })
                
                structure_univers['chips'][chip] = structure_chip
            
            structure_complete[univers] = structure_univers
        
        # 3. Vérifier la disposition verticale spécifique pour Mundo
        print(f"\n=== VERIFICATION DISPOSITION VERTICALE MUNDO ===")
        cursor.execute("""
            SELECT 
                chip,
                ligne,
                colonne,
                forme,
                petique,
                denomination
            FROM table_de_katula 
            WHERE univers = 'mundo' AND chip IN ('chip1', 'chip2', 'chip3')
            ORDER BY chip, ligne, colonne
        """)
        
        mundo_details = cursor.fetchall()
        
        current_chip = None
        for chip, ligne, colonne, forme, petique, denomination in mundo_details:
            if chip != current_chip:
                print(f"\n{chip} (disposition verticale):")
                current_chip = chip
            print(f"  {ligne}-{colonne}: {forme} | Petique: {petique} | Denom: {denomination}")
        
        # 4. Analyser les 4 cellules verticales pour chaque chip Mundo
        print(f"\n=== ANALYSE 4 CELLULES VERTICALES MUNDO ===")
        cursor.execute("""
            SELECT DISTINCT chip FROM table_de_katula WHERE univers = 'mundo' ORDER BY chip LIMIT 5
        """)
        mundo_chips = [c[0] for c in cursor.fetchall()]
        
        for chip in mundo_chips:
            cursor.execute("""
                SELECT ligne, colonne, forme, petique, denomination
                FROM table_de_katula 
                WHERE univers = 'mundo' AND chip = %s
                ORDER BY ligne, colonne
            """, (chip,))
            
            cellules = cursor.fetchall()
            print(f"\n{chip} - {len(cellules)} cellules:")
            
            formes_ordre = ['carre', 'triangle', 'cercle', 'rectangle']
            for i, (ligne, colonne, forme, petique, denomination) in enumerate(cellules):
                position_verticale = i + 1
                print(f"  Cellule {position_verticale}: {forme} ({ligne}-{colonne}) | {petique} | {denomination}")
        
        # 5. Sauvegarder la structure complète
        with open('katula_structure_reelle.json', 'w', encoding='utf-8') as f:
            json.dump(structure_complete, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== STRUCTURE SAUVEGARDEE ===")
        print("Fichier: katula_structure_reelle.json")
        
        # 6. Générer le service pour exploiter cette structure
        generate_real_katula_service()
        
        cursor.close()
        conn.close()
        
        return structure_complete
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def generate_real_katula_service():
    """Générer un service pour exploiter la vraie structure Katula"""
    
    service_code = '''"""
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
'''
    
    with open('app/services/real_katula_service.py', 'w', encoding='utf-8') as f:
        f.write(service_code)
    
    print("Service généré: app/services/real_katula_service.py")

if __name__ == "__main__":
    structure = analyze_real_katula_structure()
    if structure:
        print("\n✅ Analyse terminée avec succès!")
        print("📁 Structure sauvegardée dans katula_structure_reelle.json")
        print("🔧 Service généré dans app/services/real_katula_service.py")