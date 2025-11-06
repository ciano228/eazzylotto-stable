"""
Service avancé pour la vraie table Katula multi-dimensionnelle
"""
import os
import psycopg2
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AdvancedKatulaService:
    
    @staticmethod
    def get_db_connection():
        """Obtenir une connexion à la vraie base de données"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        return psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
    
    @staticmethod
    def get_complete_katula_table(universe: str) -> Dict[str, Any]:
        """Récupérer la vraie table Katula avec toute sa complexité"""
        try:
            conn = AdvancedKatulaService.get_db_connection()
            cursor = conn.cursor()
            
            # Récupérer toutes les données pour l'univers
            cursor.execute("""
                SELECT chip_id, ligne, colonne, petique, chip, forme, denomination
                FROM combinations 
                WHERE univers = %s
                ORDER BY ligne, colonne, forme
            """, (universe,))
            
            katula_data = cursor.fetchall()
            
            if not katula_data:
                return AdvancedKatulaService._get_fallback_data(universe)
            
            # Organiser les données par position
            positions_data = {}
            all_formes = set()
            all_denominations = set()
            petiques_count = {}
            
            for row in katula_data:
                chip_id, ligne, colonne, petique, chip, forme, denomination = row
                position_key = f"{ligne}-{colonne}"
                
                if position_key not in positions_data:
                    positions_data[position_key] = {
                        "ligne": ligne,
                        "colonne": colonne,
                        "chip_name": chip,
                        "petique": petique,
                        "formes": {},
                        "all_denominations": []
                    }
                
                # Ajouter la forme et sa dénomination
                if forme:
                    positions_data[position_key]["formes"][forme] = denomination
                    all_formes.add(forme)
                
                if denomination:
                    positions_data[position_key]["all_denominations"].append(denomination)
                    all_denominations.add(denomination)
                
                # Compter les pétiques
                petiques_count[petique] = petiques_count.get(petique, 0) + 1
            
            # Créer la matrice enrichie 8x6
            matrix = []
            chip_positions = {}
            
            for row in range(8):
                matrix_row = []
                for col in range(6):
                    ligne_key = f"L{row+1}"
                    colonne_key = f"C{col+1}"
                    position_key = f"{ligne_key}-{colonne_key}"
                    chip_number = row * 6 + col + 1
                    
                    if position_key in positions_data:
                        pos_data = positions_data[position_key]
                        
                        cell_data = {
                            "chip_number": chip_number,
                            "position": f"{row+1}-{col+1}",
                            "chip_name": pos_data["chip_name"],
                            "petique": pos_data["petique"],
                            "formes": pos_data["formes"],
                            "denominations": pos_data["all_denominations"],
                            "forme_count": len(pos_data["formes"]),
                            "primary_forme": list(pos_data["formes"].keys())[0] if pos_data["formes"] else "unknown"
                        }
                        
                        matrix_row.append(cell_data)
                        
                        chip_positions[f"chip_{chip_number}"] = {
                            "chip_number": chip_number,
                            "position": f"{row+1}-{col+1}",
                            "row": row + 1,
                            "column": col + 1,
                            "geometric_zone": pos_data["petique"],
                            "chip_name": pos_data["chip_name"],
                            "formes": pos_data["formes"],
                            "denominations": pos_data["all_denominations"],
                            "complexity_level": len(pos_data["formes"])
                        }
                    else:
                        # Position vide
                        cell_data = {
                            "chip_number": chip_number,
                            "position": f"{row+1}-{col+1}",
                            "chip_name": f"chip{chip_number}",
                            "petique": "unknown",
                            "formes": {},
                            "denominations": [],
                            "forme_count": 0,
                            "primary_forme": "empty"
                        }
                        matrix_row.append(cell_data)
                
                matrix.append(matrix_row)
            
            # Récupérer les tables spécialisées pour cet univers
            specialized_tables = AdvancedKatulaService._get_specialized_tables(cursor, universe)
            
            cursor.close()
            conn.close()
            
            return {
                "universe": universe,
                "matrix": matrix,
                "chip_positions": chip_positions,
                "statistics": {
                    "total_entries": len(katula_data),
                    "unique_positions": len(positions_data),
                    "total_formes": list(all_formes),
                    "total_denominations": len(all_denominations),
                    "petiques_distribution": petiques_count,
                    "complexity_score": len(katula_data) / max(len(positions_data), 1)
                },
                "specialized_tables": specialized_tables,
                "last_updated": datetime.now().isoformat(),
                "total_chips": len(chip_positions),
                "status": "active",
                "data_source": "real_advanced_database"
            }
            
        except Exception as e:
            print(f"Erreur accès base avancée: {e}")
            return AdvancedKatulaService._get_fallback_data(universe)
    
    @staticmethod
    def _get_specialized_tables(cursor, universe: str) -> Dict[str, Any]:
        """Récupérer les données des tables spécialisées"""
        specialized_data = {}
        
        # Chercher les tables pour cet univers
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE %s
            ORDER BY table_name
        """, (f'combinations_{universe}_%',))
        
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Récupérer quelques exemples
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    examples = cursor.fetchall()
                    
                    # Récupérer les colonnes
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        ORDER BY ordinal_position
                    """)
                    columns = [c[0] for c in cursor.fetchall()]
                    
                    specialized_data[table_name] = {
                        "count": count,
                        "columns": columns,
                        "examples": examples
                    }
            except Exception as e:
                print(f"Erreur table {table_name}: {e}")
        
        return specialized_data
    
    @staticmethod
    def get_forme_analysis(universe: str, forme: str = None) -> Dict[str, Any]:
        """Analyser les formes pour un univers"""
        try:
            conn = AdvancedKatulaService.get_db_connection()
            cursor = conn.cursor()
            
            if forme:
                cursor.execute("""
                    SELECT ligne, colonne, chip, denomination, petique
                    FROM combinations 
                    WHERE univers = %s AND forme = %s
                    ORDER BY ligne, colonne
                """, (universe, forme))
            else:
                cursor.execute("""
                    SELECT forme, COUNT(*) as count, 
                           array_agg(DISTINCT denomination) as denominations
                    FROM combinations 
                    WHERE univers = %s 
                    GROUP BY forme
                    ORDER BY count DESC
                """, (universe,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {
                "universe": universe,
                "forme": forme,
                "results": results,
                "analysis_type": "specific_forme" if forme else "all_formes"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_fallback_data(universe: str) -> Dict[str, Any]:
        """Données de secours simplifiées"""
        return {
            "universe": universe,
            "matrix": [],
            "chip_positions": {},
            "statistics": {"error": "Données non disponibles"},
            "last_updated": datetime.now().isoformat(),
            "total_chips": 0,
            "status": "fallback",
            "data_source": "error_fallback"
        }