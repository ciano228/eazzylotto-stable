"""
Service de Génération de Numéros
Convertit les attributs en paires de numéros réels (25-65, 35-42, etc.)
"""
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import random

class NumberGeneratorService:
    """
    Service pour générer des paires de numéros basées sur les attributs
    """
    
    @staticmethod
    def convert_attributes_to_numbers(
        db: Session, 
        attributes: Dict[str, str], 
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """Convertit les attributs en paires de numéros réels"""
        
        try:
            # Construire la requête pour trouver les combinaisons correspondantes
            conditions = []
            params = {"universe": universe}
            
            for attr_name, attr_value in attributes.items():
                if attr_value and attr_value != "N/A":
                    conditions.append(f"{attr_name} = :{attr_name}")
                    params[attr_name] = attr_value
            
            if not conditions:
                return NumberGeneratorService._generate_random_numbers()
            
            # Requête pour trouver les combinaisons correspondantes
            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT num1, num2, combination_id
                FROM combinations 
                WHERE univers = :universe 
                AND {where_clause}
                ORDER BY combination_id DESC
                LIMIT 10
            """
            
            result = db.execute(text(query), params)
            combinations = result.fetchall()
            
            if combinations:
                # Retourner les vraies combinaisons trouvées
                number_pairs = []
                for combo in combinations:
                    number_pairs.append({
                        "num1": combo.num1,
                        "num2": combo.num2,
                        "pair": f"{combo.num1}-{combo.num2}",
                        "combination_id": combo.combination_id,
                        "source": "historical_match"
                    })
                
                return {
                    "success": True,
                    "method": "historical_lookup",
                    "attributes_used": attributes,
                    "number_pairs": number_pairs,
                    "total_found": len(number_pairs)
                }
            else:
                # Générer des numéros basés sur les attributs similaires
                return NumberGeneratorService._generate_similar_numbers(db, attributes, universe)
                
        except Exception as e:
            print(f"❌ Erreur conversion attributs->numéros: {e}")
            return NumberGeneratorService._generate_random_numbers()
    
    @staticmethod
    def _generate_similar_numbers(
        db: Session, 
        attributes: Dict[str, str], 
        universe: str
    ) -> Dict[str, Any]:
        """Génère des numéros basés sur des attributs similaires"""
        
        try:
            # Chercher des combinaisons avec au moins quelques attributs similaires
            similar_pairs = []
            
            for attr_name, attr_value in attributes.items():
                if attr_value and attr_value != "N/A":
                    query = f"""
                        SELECT num1, num2, {attr_name}
                        FROM combinations 
                        WHERE univers = :universe 
                        AND {attr_name} = :attr_value
                        ORDER BY combination_id DESC
                        LIMIT 5
                    """
                    
                    result = db.execute(text(query), {
                        "universe": universe, 
                        "attr_value": attr_value
                    })
                    
                    for row in result.fetchall():
                        similar_pairs.append({
                            "num1": row.num1,
                            "num2": row.num2,
                            "pair": f"{row.num1}-{row.num2}",
                            "matching_attribute": attr_name,
                            "matching_value": attr_value,
                            "source": "similar_attribute"
                        })
            
            if similar_pairs:
                # Supprimer les doublons
                unique_pairs = []
                seen_pairs = set()
                
                for pair in similar_pairs:
                    pair_key = f"{pair['num1']}-{pair['num2']}"
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        unique_pairs.append(pair)
                
                return {
                    "success": True,
                    "method": "similar_attributes",
                    "attributes_used": attributes,
                    "number_pairs": unique_pairs[:5],  # Top 5
                    "total_found": len(unique_pairs)
                }
            else:
                return NumberGeneratorService._generate_random_numbers()
                
        except Exception as e:
            print(f"❌ Erreur génération similaire: {e}")
            return NumberGeneratorService._generate_random_numbers()
    
    @staticmethod
    def _generate_random_numbers() -> Dict[str, Any]:
        """Génère des paires de numéros aléatoires optimisées"""
        
        # Générer 5 paires aléatoires dans des plages réalistes
        number_pairs = []
        
        for i in range(5):
            # Générer des numéros dans des plages typiques de loterie
            num1 = random.randint(1, 49)
            num2 = random.randint(1, 49)
            
            # S'assurer que num1 < num2
            if num1 > num2:
                num1, num2 = num2, num1
            elif num1 == num2:
                num2 = min(49, num2 + 1)
            
            number_pairs.append({
                "num1": num1,
                "num2": num2,
                "pair": f"{num1}-{num2}",
                "source": "optimized_random"
            })
        
        return {
            "success": True,
            "method": "optimized_random",
            "attributes_used": {},
            "number_pairs": number_pairs,
            "total_found": len(number_pairs)
        }
    
    @staticmethod
    def generate_numbers_from_combination(
        db: Session,
        combination_data: Dict[str, Any],
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """Génère des numéros à partir d'une combinaison complète"""
        
        try:
            attributes = combination_data.get("attributes", {})
            strategy = combination_data.get("strategy", "unknown")
            
            # Convertir les attributs en numéros
            number_result = NumberGeneratorService.convert_attributes_to_numbers(
                db, attributes, universe
            )
            
            # Ajouter les informations de la combinaison originale
            number_result.update({
                "original_combination": combination_data,
                "generation_strategy": strategy,
                "conversion_timestamp": datetime.now().isoformat()
            })
            
            return number_result
            
        except Exception as e:
            print(f"❌ Erreur génération numéros: {e}")
            return {
                "success": False,
                "error": str(e),
                "number_pairs": []
            }
    
    @staticmethod
    def batch_generate_numbers(
        db: Session,
        combinations: List[Dict[str, Any]],
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """Génère des numéros pour plusieurs combinaisons"""
        
        results = []
        
        for i, combination in enumerate(combinations):
            try:
                number_result = NumberGeneratorService.generate_numbers_from_combination(
                    db, combination, universe
                )
                
                results.append({
                    "combination_index": i,
                    "combination_id": combination.get("id", f"combo_{i}"),
                    "number_generation": number_result
                })
                
            except Exception as e:
                results.append({
                    "combination_index": i,
                    "combination_id": combination.get("id", f"combo_{i}"),
                    "error": str(e)
                })
        
        successful_results = [r for r in results if "error" not in r]
        
        return {
            "universe": universe,
            "total_combinations": len(combinations),
            "successful_conversions": len(successful_results),
            "failed_conversions": len(combinations) - len(successful_results),
            "results": results,
            "batch_timestamp": datetime.now().isoformat()
        }