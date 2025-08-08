"""
Service pour gérer les formes par univers
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class FormeService:
    """Service pour récupérer les formes spécifiques à chaque univers"""
    
    @staticmethod
    def get_formes_by_universe(universe: str, db: Session = None) -> Dict:
        """
        Récupère les formes disponibles pour un univers spécifique
        
        Args:
            universe: Nom de l'univers (mundo, fruity, trigga, roaster, sunshine)
            db: Session de base de données
            
        Returns:
            Dict contenant les formes ordonnées et leurs informations
        """
        try:
            logger.info(f"Récupération formes pour {universe}, db={db is not None}")
            
            if not db:
                # Si pas de DB, utiliser les formes par défaut
                logger.warning(f"Pas de session DB pour {universe}, utilisation des formes par défaut")
                formes = FormeService._get_default_formes(universe)
            else:
                # Requête pour récupérer les formes distinctes pour cet univers
                query = text("""
                SELECT DISTINCT forme 
                FROM combinations 
                WHERE univers = :universe 
                AND forme IS NOT NULL 
                AND forme != ''
                ORDER BY forme
                """)
                
                logger.info(f"Exécution requête pour {universe}")
                result = db.execute(query, {"universe": universe})
                formes = [row[0] for row in result.fetchall()]
                logger.info(f"Formes trouvées en DB pour {universe}: {formes}")
                
                # Si aucune forme trouvée en DB, utiliser les formes par défaut
                if not formes:
                    logger.warning(f"Aucune forme trouvée en DB pour {universe}, utilisation des formes par défaut")
                    formes = FormeService._get_default_formes(universe)
            
            # Organiser les formes selon l'ordre logique
            ordered_formes = FormeService._order_formes(formes, universe)
            
            # Compter les occurrences de chaque forme
            forme_counts = FormeService._count_formes(universe, ordered_formes, db) if db else {}
            
            # Filtrer les formes qui ont des données (pour Sunshine notamment)
            if universe == "sunshine":
                ordered_formes = FormeService._filter_formes_with_data(ordered_formes, forme_counts)
            
            return {
                "universe": universe,
                "formes": ordered_formes,
                "total_formes": len(ordered_formes),
                "forme_counts": forme_counts,
                "is_variable_geometry": len(ordered_formes) > 4
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération formes {universe}: {e}")
            return {
                "universe": universe,
                "formes": FormeService._get_default_formes(universe),
                "total_formes": 4,
                "forme_counts": {},
                "is_variable_geometry": False,
                "error": str(e)
            }
    
    @staticmethod
    def _order_formes(formes: List[str], universe: str) -> List[str]:
        """
        Ordonne les formes selon l'ordre exact spécifié
        
        Args:
            formes: Liste des formes trouvées en DB
            universe: Nom de l'univers
            
        Returns:
            Liste des formes ordonnées selon l'ordre exact requis
        """
        # ORDRE EXACT REQUIS (selon spécification)
        exact_order = [
            # 4 formes de base
            "carre", "triangle", "cercle", "rectangle",
            # Combinaisons avec carré
            "carre-triangle", "carre-cercle", "carre-rectangle",
            # Combinaisons avec triangle  
            "triangle-carre", "triangle-cercle", "triangle-rectangle",
            # Combinaisons avec cercle
            "cercle-carre", "cercle-triangle", "cercle-rectangle", 
            # Combinaisons avec rectangle
            "rectangle-carre", "rectangle-triangle", "rectangle-cercle"
        ]
        
        ordered = []
        
        # Ajouter les formes dans l'ordre exact spécifié
        for forme in exact_order:
            if forme in formes:
                ordered.append(forme)
        
        # Ajouter les formes restantes non prévues (au cas où)
        for forme in formes:
            if forme not in ordered:
                ordered.append(forme)
        
        return ordered
    
    @staticmethod
    def _count_formes(universe: str, formes: List[str], db: Session = None) -> Dict[str, int]:
        """
        Compte le nombre d'occurrences de chaque forme
        
        Args:
            universe: Nom de l'univers
            formes: Liste des formes à compter
            db: Session de base de données
            
        Returns:
            Dict avec le nombre d'occurrences par forme
        """
        try:
            if not db:
                return {forme: 0 for forme in formes}
                
            counts = {}
            
            for forme in formes:
                query = text("""
                SELECT COUNT(*) 
                FROM combinations 
                WHERE univers = :universe AND forme = :forme
                """)
                result = db.execute(query, {"universe": universe, "forme": forme})
                count = result.fetchone()[0]
                counts[forme] = count
            
            return counts
            
        except Exception as e:
            logger.error(f"Erreur comptage formes {universe}: {e}")
            return {forme: 0 for forme in formes}
    
    @staticmethod
    def _get_default_formes(universe: str) -> List[str]:
        """
        Retourne les formes par défaut selon l'univers
        
        Args:
            universe: Nom de l'univers
            
        Returns:
            Liste des formes par défaut
        """
        if universe == "trigga":
            # Trigga : 4 simples + 12 combinées = 16 formes
            return [
                "carre", "triangle", "cercle", "rectangle",
                "carre-triangle", "carre-cercle", "carre-rectangle",
                "triangle-carre", "triangle-cercle", "triangle-rectangle",
                "cercle-carre", "cercle-triangle", "cercle-rectangle",
                "rectangle-carre", "rectangle-triangle", "rectangle-cercle"
            ]
        elif universe == "roaster":
            # Roaster : 12 formes composées seulement (sans les 4 simples)
            return [
                "carre-triangle", "carre-cercle", "carre-rectangle",
                "triangle-carre", "triangle-cercle", "triangle-rectangle",
                "cercle-carre", "cercle-triangle", "cercle-rectangle",
                "rectangle-carre", "rectangle-triangle", "rectangle-cercle"
            ]
        elif universe == "sunshine":
            # Sunshine : 16 formes (comme Trigga, à vérifier lesquelles ont des données)
            return [
                "carre", "triangle", "cercle", "rectangle",
                "carre-triangle", "carre-cercle", "carre-rectangle",
                "triangle-carre", "triangle-cercle", "triangle-rectangle",
                "cercle-carre", "cercle-triangle", "cercle-rectangle",
                "rectangle-carre", "rectangle-triangle", "rectangle-cercle"
            ]
        else:
            # Mundo et Fruity : 4 formes de base
            return ["carre", "triangle", "cercle", "rectangle"]
    
    @staticmethod
    def get_chip_formes(universe: str, chip_number: int, db: Session = None) -> Dict:
        """
        Récupère les formes présentes sur un chip spécifique avec leurs dénominations
        
        Args:
            universe: Nom de l'univers
            chip_number: Numéro du chip (1-48)
            db: Session de base de données
            
        Returns:
            Dict avec les formes et leurs données pour ce chip
        """
        try:
            if not db:
                return {
                    "universe": universe,
                    "chip_number": chip_number,
                    "formes_data": {},
                    "total_formes": 0,
                    "error": "Pas de session DB"
                }
            
            query = text("""
            SELECT forme, denomination, COUNT(*) as count
            FROM combinations 
            WHERE univers = :universe AND chip = :chip_number
            GROUP BY forme, denomination
            ORDER BY forme, denomination
            """)
            
            result = db.execute(query, {"universe": universe, "chip_number": f"chip{chip_number}"})
            results = result.fetchall()
            
            # Organiser par forme
            formes_data = {}
            for row in results:
                forme, denomination, count = row
                if forme not in formes_data:
                    formes_data[forme] = []
                formes_data[forme].append({
                    "denomination": denomination,
                    "count": count
                })
            
            return {
                "universe": universe,
                "chip_number": chip_number,
                "formes_data": formes_data,
                "total_formes": len(formes_data)
            }
            
        except Exception as e:
            logger.error(f"Erreur formes chip {chip_number} {universe}: {e}")
            return {
                "universe": universe,
                "chip_number": chip_number,
                "formes_data": {},
                "total_formes": 0,
                "error": str(e)
            }
    
    @staticmethod
    def get_denomination_details(universe: str, denomination: str, db: Session = None) -> Dict:
        """
        Récupère les détails complets d'une dénomination spécifique
        
        Args:
            universe: Nom de l'univers
            denomination: Dénomination complète (ex: "road 1", "house 1")
            db: Session de base de données
            
        Returns:
            Dict avec tous les détails de la dénomination
        """
        try:
            if not db:
                return {
                    "universe": universe,
                    "denomination": denomination,
                    "details": [],
                    "error": "Pas de session DB"
                }
            
            query = text("""
            SELECT 
                chip, forme, denomination, engine, beastie, tome, parite, unidos,
                num1, num2, date_tirage
            FROM combinations 
            WHERE univers = :universe AND denomination = :denomination
            ORDER BY date_tirage DESC
            LIMIT 20
            """)
            
            result = db.execute(query, {"universe": universe, "denomination": denomination})
            results = result.fetchall()
            
            details = []
            for row in results:
                details.append({
                    "chip": row[0],
                    "forme": row[1],
                    "denomination": row[2],
                    "engine": row[3],
                    "beastie": row[4],
                    "tome": row[5],
                    "parite": row[6],
                    "unidos": row[7],
                    "num1": row[8],
                    "num2": row[9],
                    "date_tirage": str(row[10]) if row[10] else None
                })
            
            return {
                "universe": universe,
                "denomination": denomination,
                "total_occurrences": len(details),
                "details": details
            }
            
        except Exception as e:
            logger.error(f"Erreur détails dénomination {denomination} {universe}: {e}")
            return {
                "universe": universe,
                "denomination": denomination,
                "details": [],
                "error": str(e)
            }
    
    @staticmethod
    def get_all_universes_formes() -> Dict:
        """
        Récupère les formes pour tous les univers
        
        Returns:
            Dict avec les formes de tous les univers
        """
        universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
        all_formes = {}
        
        for universe in universes:
            all_formes[universe] = FormeService.get_formes_by_universe(universe)
        
        return {
            "universes": all_formes,
            "summary": {
                universe: data["total_formes"] 
                for universe, data in all_formes.items()
            }
        }   
 
    @staticmethod
    def _filter_formes_with_data(formes: List[str], forme_counts: Dict[str, int]) -> List[str]:
        """
        Filtre les formes qui ont réellement des données
        
        Args:
            formes: Liste des formes à filtrer
            forme_counts: Nombre d'occurrences par forme
            
        Returns:
            Liste des formes qui ont des données (count > 0)
        """
        return [forme for forme in formes if forme_counts.get(forme, 0) > 0]
    
    @staticmethod
    def get_formes_statistics() -> Dict:
        """
        Récupère les statistiques des formes pour tous les univers
        
        Returns:
            Dict avec les statistiques par univers
        """
        universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
        stats = {}
        
        for universe in universes:
            try:
                formes_data = FormeService.get_formes_by_universe(universe)
                stats[universe] = {
                    "total_formes": formes_data["total_formes"],
                    "is_variable_geometry": formes_data["is_variable_geometry"],
                    "formes_list": formes_data["formes"][:5],  # Premiers 5 pour aperçu
                    "has_combined_formes": any("-" in forme for forme in formes_data["formes"])
                }
            except Exception as e:
                stats[universe] = {"error": str(e)}
        
        return {
            "universes_statistics": stats,
            "summary": {
                "total_universes": len(universes),
                "variable_geometry_universes": len([u for u, s in stats.items() if s.get("is_variable_geometry", False)]),
                "combined_formes_universes": len([u for u, s in stats.items() if s.get("has_combined_formes", False)])
            }
        }