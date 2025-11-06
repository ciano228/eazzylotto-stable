#!/usr/bin/env python3
"""
Analyse détaillée de la structure Katula par univers
"""
import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()

def analyze_katula_structure():
    """Analyser la structure complète des compartiments Katula"""
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
        
        print("=== ANALYSE STRUCTURE KATULA DETAILLEE ===\n")
        
        # 1. Structure générale par univers
        cursor.execute("""
            SELECT 
                univers,
                COUNT(*) as total_entries,
                COUNT(DISTINCT chip) as unique_chips,
                COUNT(DISTINCT forme) as unique_formes,
                COUNT(DISTINCT granque) as unique_granques,
                COUNT(DISTINCT tome) as unique_tomes
            FROM table_de_katula 
            WHERE univers IS NOT NULL
            GROUP BY univers 
            ORDER BY univers
        """)
        
        universes_stats = cursor.fetchall()
        
        print("STATISTIQUES PAR UNIVERS:")
        for univers, total, chips, formes, granques, tomes in universes_stats:
            print(f"  {univers.upper()}:")
            print(f"    - Total entrées: {total}")
            print(f"    - Chips uniques: {chips}")
            print(f"    - Formes uniques: {formes}")
            print(f"    - Granques uniques: {granques}")
            print(f"    - Tomes uniques: {tomes}")
        
        # 2. Structure détaillée par univers
        structure_complete = {}
        
        for univers, _, _, _, _, _ in universes_stats:
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
            
            # Structure par chip
            cursor.execute("""
                SELECT 
                    chip,
                    COUNT(*) as nb_compartiments,
                    array_agg(DISTINCT forme ORDER BY forme) as formes_chip,
                    array_agg(DISTINCT granque ORDER BY granque) as granques_chip,
                    array_agg(DISTINCT tome ORDER BY tome) as tomes_chip
                FROM table_de_katula 
                WHERE univers = %s 
                GROUP BY chip 
                ORDER BY chip::integer
                LIMIT 10
            """, (univers,))
            
            chips_structure = cursor.fetchall()
            
            structure_univers = {
                'formes_disponibles': formes,
                'chips': {}
            }
            
            print(f"Structure des premiers chips:")
            for chip, nb_comp, formes_chip, granques_chip, tomes_chip in chips_structure:
                print(f"  Chip {chip}: {nb_comp} compartiments")
                print(f"    Formes: {formes_chip}")
                print(f"    Granques: {granques_chip}")
                print(f"    Tomes: {tomes_chip}")
                
                # Détail des compartiments pour ce chip
                cursor.execute("""
                    SELECT forme, granque, tome, denomination, position
                    FROM table_de_katula 
                    WHERE univers = %s AND chip = %s
                    ORDER BY forme, granque, tome
                """, (univers, chip))
                
                compartiments = cursor.fetchall()
                
                structure_chip = {
                    'nb_compartiments': nb_comp,
                    'formes': formes_chip,
                    'granques': granques_chip,
                    'tomes': tomes_chip,
                    'compartiments': []
                }
                
                for forme, granque, tome, denomination, position in compartiments:
                    structure_chip['compartiments'].append({
                        'forme': forme,
                        'granque': granque,
                        'tome': tome,
                        'denomination': denomination,
                        'position': position
                    })
                
                structure_univers['chips'][chip] = structure_chip
            
            structure_complete[univers] = structure_univers
        
        # 3. Vérifier la disposition verticale pour Mundo
        print(f"\n=== VERIFICATION DISPOSITION VERTICALE MUNDO ===")
        cursor.execute("""
            SELECT 
                chip,
                forme,
                position,
                granque,
                tome,
                denomination
            FROM table_de_katula 
            WHERE univers = 'mundo' AND chip IN ('1', '2', '3')
            ORDER BY chip::integer, position, forme
        """)
        
        mundo_details = cursor.fetchall()
        
        current_chip = None
        for chip, forme, position, granque, tome, denomination in mundo_details:
            if chip != current_chip:
                print(f"\nChip {chip} (disposition verticale):")
                current_chip = chip
            print(f"  Position {position}: {forme} | Granque: {granque} | Tome: {tome} | Denom: {denomination}")
        
        # 4. Sauvegarder la structure complète
        with open('katula_structure_complete.json', 'w', encoding='utf-8') as f:
            json.dump(structure_complete, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== STRUCTURE SAUVEGARDEE ===")
        print("Fichier: katula_structure_complete.json")
        
        # 5. Générer le service pour exploiter cette structure
        generate_katula_service(structure_complete)
        
        cursor.close()
        conn.close()
        
        return structure_complete
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def generate_katula_service(structure):
    """Générer un service pour exploiter la structure Katula"""
    
    service_code = '''"""
Service pour exploiter la structure complète des tables Katula
"""
import os
import psycopg2
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class KatulaStructureService:
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
            WHERE univers = %s 
            ORDER BY chip::integer
        """, (univers,))
        return [c[0] for c in cursor.fetchall()]
    
    def get_chip_structure(self, univers: str, chip: str) -> Dict:
        """Récupérer la structure complète d'un chip"""
        cursor = self.connection.cursor()
        
        # Structure générale
        cursor.execute("""
            SELECT 
                COUNT(*) as nb_compartiments,
                array_agg(DISTINCT forme ORDER BY forme) as formes,
                array_agg(DISTINCT granque ORDER BY granque) as granques,
                array_agg(DISTINCT tome ORDER BY tome) as tomes
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
        """, (univers, chip))
        
        result = cursor.fetchone()
        nb_comp, formes, granques, tomes = result
        
        # Compartiments détaillés
        cursor.execute("""
            SELECT forme, granque, tome, denomination, position
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
            ORDER BY position, forme
        """, (univers, chip))
        
        compartiments = []
        for forme, granque, tome, denomination, position in cursor.fetchall():
            compartiments.append({
                'forme': forme,
                'granque': granque,
                'tome': tome,
                'denomination': denomination,
                'position': position
            })
        
        return {
            'chip': chip,
            'univers': univers,
            'nb_compartiments': nb_comp,
            'formes_disponibles': formes,
            'granques_disponibles': granques,
            'tomes_disponibles': tomes,
            'compartiments': compartiments
        }
    
    def get_vertical_layout(self, univers: str, chip: str) -> List[Dict]:
        """Récupérer la disposition verticale d'un chip (4 cellules pour Mundo)"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT forme, granque, tome, denomination, position
            FROM table_de_katula 
            WHERE univers = %s AND chip = %s
            ORDER BY position
        """, (univers, chip))
        
        layout = []
        for forme, granque, tome, denomination, position in cursor.fetchall():
            layout.append({
                'position': position,
                'forme': forme,
                'granque': granque,
                'tome': tome,
                'denomination': denomination
            })
        
        return layout
    
    def get_combinations_by_chip(self, univers: str, chip: str) -> List[Dict]:
        """Récupérer les combinaisons liées à un chip"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id, c.combination_data, c.frequency
            FROM combinations c
            JOIN table_de_katula tk ON tk.chip = %s AND tk.univers = %s
            WHERE c.combination_data LIKE %s
            LIMIT 10
        """, (chip, univers, f'%{chip}%'))
        
        combinations = []
        for comb_id, data, frequency in cursor.fetchall():
            combinations.append({
                'id': comb_id,
                'data': data,
                'frequency': frequency
            })
        
        return combinations

# Instance globale
katula_service = KatulaStructureService()
'''
    
    with open('app/services/katula_structure_service.py', 'w', encoding='utf-8') as f:
        f.write(service_code)
    
    print("Service généré: app/services/katula_structure_service.py")

if __name__ == "__main__":
    structure = analyze_katula_structure()
    if structure:
        print("\n✅ Analyse terminée avec succès!")
        print("📁 Structure sauvegardée dans katula_structure_complete.json")
        print("🔧 Service généré dans app/services/katula_structure_service.py")