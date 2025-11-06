"""
Service de Découverte Automatique des Attributs
Détecte automatiquement les nouveaux attributs dans la base de données
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from datetime import datetime

class AttributeDiscoveryService:
    """
    Service pour découvrir automatiquement les attributs disponibles
    """
    
    @staticmethod
    def discover_attributes(db: Session, table_name: str = "combinations") -> List[str]:
        """Découvre automatiquement tous les attributs disponibles dans la table"""
        
        try:
            # Obtenir la structure de la table
            inspector = inspect(db.bind)
            columns = inspector.get_columns(table_name)
            
            # Filtrer les colonnes qui sont des attributs (pas les IDs, dates, etc.)
            excluded_columns = {
                'combination_id', 'num1', 'num2', 'univers', 
                'created_at', 'updated_at', 'id', 'date_tirage'
            }
            
            attribute_columns = []
            for column in columns:
                column_name = column['name']
                if column_name not in excluded_columns:
                    attribute_columns.append(column_name)
            
            print(f"🔍 Attributs découverts: {attribute_columns}")
            return sorted(attribute_columns)
            
        except Exception as e:
            print(f"❌ Erreur découverte attributs: {e}")
            # Fallback vers la liste statique
            return ['forme', 'engine', 'beastie', 'tome', 'parite', 'unidos', 'chip']
    
    @staticmethod
    def get_attribute_values(db: Session, attribute: str, universe: str = "mundo", limit: int = 100) -> List[str]:
        """Récupère les valeurs possibles pour un attribut donné"""
        
        try:
            query = f"""
                SELECT DISTINCT {attribute} as value
                FROM combinations 
                WHERE univers = :universe 
                AND {attribute} IS NOT NULL
                ORDER BY {attribute}
                LIMIT :limit
            """
            
            result = db.execute(text(query), {"universe": universe, "limit": limit})
            values = [row.value for row in result.fetchall()]
            
            return values
            
        except Exception as e:
            print(f"❌ Erreur récupération valeurs {attribute}: {e}")
            return []
    
    @staticmethod
    def analyze_attribute_types(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Analyse les types et caractéristiques de chaque attribut"""
        
        attributes = AttributeDiscoveryService.discover_attributes(db)
        analysis = {}
        
        for attribute in attributes:
            try:
                # Compter les valeurs uniques
                query_count = f"""
                    SELECT COUNT(DISTINCT {attribute}) as unique_count,
                           COUNT({attribute}) as total_count
                    FROM combinations 
                    WHERE univers = :universe 
                    AND {attribute} IS NOT NULL
                """
                
                result = db.execute(text(query_count), {"universe": universe})
                row = result.fetchone()
                
                # Récupérer quelques exemples de valeurs
                values = AttributeDiscoveryService.get_attribute_values(db, attribute, universe, 10)
                
                analysis[attribute] = {
                    "unique_values": row.unique_count if row else 0,
                    "total_entries": row.total_count if row else 0,
                    "sample_values": values[:5],  # 5 premiers exemples
                    "data_type": AttributeDiscoveryService._detect_data_type(values),
                    "completeness": (row.total_count / AttributeDiscoveryService._get_total_combinations(db, universe)) if row and row.total_count else 0
                }
                
            except Exception as e:
                print(f"❌ Erreur analyse {attribute}: {e}")
                analysis[attribute] = {
                    "error": str(e),
                    "unique_values": 0,
                    "total_entries": 0
                }
        
        return {
            "universe": universe,
            "discovered_attributes": attributes,
            "attribute_analysis": analysis,
            "total_attributes": len(attributes),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _detect_data_type(values: List[str]) -> str:
        """Détecte le type de données d'un attribut"""
        
        if not values:
            return "unknown"
        
        # Vérifier si c'est numérique
        numeric_count = 0
        for value in values:
            try:
                float(str(value))
                numeric_count += 1
            except:
                pass
        
        if numeric_count > len(values) * 0.8:
            return "numeric"
        elif len(values) < 20:  # Peu de valeurs uniques
            return "categorical"
        else:
            return "text"
    
    @staticmethod
    def _get_total_combinations(db: Session, universe: str) -> int:
        """Récupère le nombre total de combinaisons pour un univers"""
        
        try:
            query = "SELECT COUNT(*) as total FROM combinations WHERE univers = :universe"
            result = db.execute(text(query), {"universe": universe})
            row = result.fetchone()
            return row.total if row else 0
        except:
            return 0
    
    @staticmethod
    def update_ml_service_attributes(db: Session) -> Dict[str, Any]:
        """Met à jour automatiquement la liste des attributs dans MLService"""
        
        try:
            # Découvrir les attributs
            discovered_attributes = AttributeDiscoveryService.discover_attributes(db)
            
            # Ici on pourrait mettre à jour dynamiquement MLService
            # Pour l'instant, on retourne juste la liste
            
            return {
                "discovered_attributes": discovered_attributes,
                "update_needed": True,
                "recommendation": "Redémarrer les services ML avec les nouveaux attributs",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "discovered_attributes": [],
                "update_needed": False
            }