"""
Service de Matrice Katula
Gère l'extraction et la manipulation des données de la matrice Katula
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import psycopg2
from psycopg2.extras import RealDictCursor
import os


class KatulaMatrixService:
    """Service pour gérer les données de la matrice Katula"""
    
    @staticmethod
    def extract_combinations_matrix(
        db: Session, 
        universe: str = "mundo", 
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Extrait les données de combinaisons pour la matrice Katula"""
        
        try:
            # Utiliser psycopg2 directement pour plus de fiabilité
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'katooling_main_system'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Requête pour récupérer les combinaisons
            cursor.execute("""
                SELECT 
                    combination_id, num1, num2, univers, forme,
                    denomination, chip, chip_id, granque_name, tome,
                    petique, ligne, colonne, alpha_ranking
                FROM combinations
                WHERE univers = %s
                ORDER BY combination_id DESC
                LIMIT %s
            """, (universe, limit))
            
            rows = cursor.fetchall()
            
            matrix_data = []
            for row in rows:
                matrix_data.append({
                    "combination_id": row['combination_id'],
                    "numbers": [row['num1'], row['num2']],
                    "num1": row['num1'],
                    "num2": row['num2'],
                    "univers": row['univers'],
                    "forme": row['forme'],
                    "denomination": row['denomination'],
                    "chip": row['chip'],
                    "chip_id": row['chip_id'],
                    "granque_name": row['granque_name'],
                    "tome": row['tome'],
                    "petique": row['petique'],
                    "ligne": row['ligne'],
                    "colonne": row['colonne'],
                    "alpha_ranking": row['alpha_ranking']
                })
            
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "universe": universe,
                "total_combinations": len(matrix_data),
                "matrix_data": matrix_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_chip_data(universe: str, chip_number: int) -> Dict[str, Any]:
        """Récupère toutes les données pour un chip spécifique"""
        
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'katooling_main_system'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            chip_id = f"chip{chip_number}"
            
            cursor.execute("""
                SELECT *
                FROM combinations
                WHERE univers = %s AND chip = %s
                ORDER BY forme, denomination
            """, (universe, chip_id))
            
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "chip_number": chip_number,
                "chip_id": chip_id,
                "universe": universe,
                "compartments": [dict(row) for row in rows]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
