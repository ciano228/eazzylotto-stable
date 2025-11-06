"""
Service de Données Amélioré avec Vérification d'Existence
Utilise la vraie structure de données avec optimisation des instances
"""
import os
import psycopg2
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
from datetime import datetime
from .service_manager import service_manager

load_dotenv()

class EnhancedDataService:
    """Service optimisé avec gestion intelligente des connexions"""
    
    def __init__(self):
        self.connection = None
        self.last_connection_check = None
        self.connect()
    
    def connect(self):
        """Connexion optimisée à la base de données"""
        try:
            DATABASE_URL = os.getenv("DATABASE_URL")
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL non configurée")
                
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
            self.last_connection_check = datetime.now()
            print("[SUCCES] Connexion DB établie")
            
        except Exception as e:
            print(f"[ERREUR] Erreur connexion DB: {e}")
            raise
    
    def ensure_connection(self):
        """Vérifie et maintient la connexion active"""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
        except:
            print("🔄 Reconnexion DB nécessaire")
            self.connect()
    
    def get_real_structure_data(self, univers: str) -> Dict[str, Any]:
        """Récupère les données de structure réelle"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            # Statistiques générales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    COUNT(DISTINCT chip) as unique_chips,
                    COUNT(DISTINCT forme) as unique_formes,
                    COUNT(DISTINCT petique) as unique_petiques
                FROM table_de_katula 
                WHERE univers = %s
            """, (univers,))
            
            stats = cursor.fetchone()
            
            # Distribution des formes
            cursor.execute("""
                SELECT forme, COUNT(*) as count
                FROM table_de_katula 
                WHERE univers = %s AND forme IS NOT NULL
                GROUP BY forme
                ORDER BY count DESC
            """, (univers,))
            
            formes_dist = dict(cursor.fetchall())
            
            return {
                "univers": univers,
                "total_entries": stats[0],
                "unique_chips": stats[1],
                "unique_formes": stats[2],
                "unique_petiques": stats[3],
                "formes_distribution": formes_dist,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur récupération données {univers}: {e}")
            return {"error": str(e)}
        finally:
            cursor.close()
    
    def get_chip_complete_info(self, univers: str, chip: str) -> Dict[str, Any]:
        """Informations complètes d'un chip"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    ligne, colonne, forme, petique, denomination,
                    chip_id
                FROM table_de_katula 
                WHERE univers = %s AND chip = %s
                ORDER BY ligne, colonne
            """, (univers, chip))
            
            compartiments = []
            for row in cursor.fetchall():
                compartiments.append({
                    "ligne": row[0],
                    "colonne": row[1],
                    "forme": row[2],
                    "petique": row[3],
                    "denomination": row[4],
                    "chip_id": row[5],
                    "coordonnee": f"{row[0]}-{row[1]}"
                })
            
            return {
                "chip": chip,
                "univers": univers,
                "nb_compartiments": len(compartiments),
                "compartiments": compartiments
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cursor.close()

def get_enhanced_data_service() -> EnhancedDataService:
    """Factory function avec vérification d'existence"""
    return service_manager.get_service(
        "enhanced_data_service",
        EnhancedDataService
    )

# Instance globale optimisée
enhanced_data_service = get_enhanced_data_service()