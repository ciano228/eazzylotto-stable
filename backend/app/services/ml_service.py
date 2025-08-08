import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import concurrent.futures
from app.ml.models.lstm_predictor import LSTMPredictor

class MLService:
    """
    Service principal pour la gestion des modèles ML
    """
    
    @staticmethod
    def get_available_attributes() -> List[str]:
        """Retourne la liste des attributs disponibles pour ML"""
        return ['forme', 'engine', 'beastie', 'tome', 'parite', 'unidos', 'chip']
    
    @staticmethod
    def train_all_lstm_models(db: Session, universe: str = "mundo", epochs: int = 50) -> Dict[str, Any]:
        """Entraîne tous les modèles LSTM pour un univers"""
        
        print(f"🚀 Début de l'entraînement de tous les modèles LSTM pour {universe}...")
        
        attributes = MLService.get_available_attributes()
        training_results = {}
        
        for attribute in attributes:
            print(f"\n🧠 Entraînement LSTM pour {attribute}...")
            
            try:
                predictor = LSTMPredictor(attribute, universe)
                result = predictor.train(db, epochs=epochs)
                training_results[attribute] = result
                
            except Exception as e:
                print(f"❌ Erreur pour {attribute}: {e}")
                training_results[attribute] = {
                    "error": str(e),
                    "attribute_type": attribute,
                    "universe": universe,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Résumé global
        successful_trainings = len([r for r in training_results.values() if "error" not in r])
        total_trainings = len(training_results)
        
        summary = {
            "universe": universe,
            "total_models": total_trainings,
            "successful_trainings": successful_trainings,
            "failed_trainings": total_trainings - successful_trainings,
            "training_results": training_results,
            "overall_timestamp": datetime.now().isoformat()
        }
        
        print(f"\n✅ Entraînement terminé: {successful_trainings}/{total_trainings} modèles réussis")
        
        return summary
    
    @staticmethod
    def predict_all_lstm(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Génère des prédictions LSTM pour tous les attributs"""
        
        print(f"🔮 Génération des prédictions LSTM pour {universe}...")
        
        attributes = MLService.get_available_attributes()
        predictions = {}
        
        for attribute in attributes:
            try:
                predictor = LSTMPredictor(attribute, universe)
                prediction = predictor.predict_next(db)
                predictions[attribute] = prediction
                
            except Exception as e:
                print(f"❌ Erreur prédiction {attribute}: {e}")
                predictions[attribute] = {
                    "error": str(e),
                    "attribute_type": attribute,
                    "universe": universe,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Résumé des prédictions
        successful_predictions = len([p for p in predictions.values() if "error" not in p])
        total_predictions = len(predictions)
        
        # Extraire les meilleures prédictions
        top_predictions = []
        for attribute, prediction in predictions.items():
            if "error" not in prediction and prediction.get("predictions"):
                top_pred = prediction["predictions"][0]  # Meilleure prédiction
                top_predictions.append({
                    "attribute_type": attribute,
                    "predicted_value": top_pred["predicted_value"],
                    "confidence": top_pred["confidence"],
                    "confidence_percent": top_pred["confidence_percent"],
                    "model_type": "LSTM"
                })
        
        # Trier par confiance décroissante
        top_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        result = {
            "universe": universe,
            "model_type": "LSTM_Neural_Network",
            "total_predictions": total_predictions,
            "successful_predictions": successful_predictions,
            "failed_predictions": total_predictions - successful_predictions,
            "top_predictions": top_predictions[:10],  # Top 10
            "detailed_predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Prédictions LSTM terminées: {successful_predictions}/{total_predictions} réussies")
        
        return result
    
    @staticmethod
    def evaluate_all_models(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Évalue tous les modèles LSTM"""
        
        print(f"📊 Évaluation de tous les modèles LSTM pour {universe}...")
        
        attributes = MLService.get_available_attributes()
        evaluations = {}
        
        for attribute in attributes:
            try:
                predictor = LSTMPredictor(attribute, universe)
                evaluation = predictor.evaluate_model(db)
                evaluations[attribute] = evaluation
                
            except Exception as e:
                print(f"❌ Erreur évaluation {attribute}: {e}")
                evaluations[attribute] = {
                    "error": str(e),
                    "attribute_type": attribute,
                    "universe": universe
                }
        
        # Calculer les métriques moyennes
        successful_evals = [e for e in evaluations.values() if "error" not in e]
        
        if successful_evals:
            avg_accuracy = sum(e["test_accuracy"] for e in successful_evals) / len(successful_evals)
            avg_loss = sum(e["test_loss"] for e in successful_evals) / len(successful_evals)
        else:
            avg_accuracy = 0
            avg_loss = 0
        
        summary = {
            "universe": universe,
            "total_models": len(attributes),
            "evaluated_models": len(successful_evals),
            "average_accuracy": round(avg_accuracy, 3),
            "average_loss": round(avg_loss, 3),
            "model_evaluations": evaluations,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Évaluation terminée - Précision moyenne: {avg_accuracy:.3f}")
        
        return summary
    
    @staticmethod
    def get_model_status(universe: str = "mundo") -> Dict[str, Any]:
        """Vérifie le statut de tous les modèles"""
        
        attributes = MLService.get_available_attributes()
        model_status = {}
        
        for attribute in attributes:
            try:
                predictor = LSTMPredictor(attribute, universe)
                
                # Vérifier si les fichiers de modèle existent
                model_path = f"backend/app/ml/models/saved/{universe}_{attribute}_lstm.h5"
                encoder_path = f"backend/app/ml/models/saved/{universe}_{attribute}_encoder.pkl"
                
                model_file_exists = os.path.exists(model_path)
                encoder_file_exists = os.path.exists(encoder_path)
                
                model_exists = model_file_exists and encoder_file_exists
                
                model_status[attribute] = {
                    "model_exists": model_exists,
                    "model_file_exists": model_file_exists,
                    "encoder_file_exists": encoder_file_exists,
                    "model_path": model_path,
                    "encoder_path": encoder_path,
                    "ready_for_prediction": model_exists
                }
                
            except Exception as e:
                model_status[attribute] = {
                    "model_exists": False,
                    "model_file_exists": False,
                    "encoder_file_exists": False,
                    "error": str(e),
                    "ready_for_prediction": False
                }
        
        # Résumé global
        ready_models = len([s for s in model_status.values() if s.get("ready_for_prediction", False)])
        total_models = len(model_status)
        
        return {
            "universe": universe,
            "total_models": total_models,
            "ready_models": ready_models,
            "models_to_train": total_models - ready_models,
            "model_details": model_status,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def combine_predictions(lstm_predictions: Dict, traditional_predictions: Dict) -> Dict[str, Any]:
        """Combine les prédictions LSTM avec les prédictions traditionnelles"""
        
        print("🔄 Combinaison des prédictions LSTM et traditionnelles...")
        
        combined_predictions = []
        
        # Extraire les prédictions LSTM
        if "top_predictions" in lstm_predictions:
            for pred in lstm_predictions["top_predictions"]:
                combined_predictions.append({
                    "attribute_type": pred["attribute_type"],
                    "predicted_value": pred["predicted_value"],
                    "lstm_confidence": pred["confidence"],
                    "lstm_confidence_percent": pred["confidence_percent"],
                    "traditional_confidence": 0,
                    "combined_score": pred["confidence"] * 0.7,  # Poids LSTM: 70%
                    "source": "LSTM_Primary"
                })
        
        # Ajouter les prédictions traditionnelles si disponibles
        if "overdue_attributes" in traditional_predictions:
            for attr_type, attributes in traditional_predictions["overdue_attributes"].items():
                for attr in attributes[:2]:  # Top 2 par type
                    # Chercher si déjà présent dans LSTM
                    existing = next((p for p in combined_predictions 
                                   if p["attribute_type"] == attr_type 
                                   and p["predicted_value"] == attr["value"]), None)
                    
                    if existing:
                        # Combiner les scores
                        traditional_score = min(1.0, attr["delay_ratio"] / 10)
                        existing["traditional_confidence"] = traditional_score
                        existing["combined_score"] = (existing["lstm_confidence"] * 0.7 + 
                                                    traditional_score * 0.3)
                        existing["source"] = "LSTM_Traditional_Combined"
                    else:
                        # Ajouter comme prédiction traditionnelle
                        traditional_score = min(1.0, attr["delay_ratio"] / 10)
                        combined_predictions.append({
                            "attribute_type": attr_type,
                            "predicted_value": attr["value"],
                            "lstm_confidence": 0,
                            "lstm_confidence_percent": 0,
                            "traditional_confidence": traditional_score,
                            "combined_score": traditional_score * 0.3,  # Poids traditionnel: 30%
                            "source": "Traditional_Only"
                        })
        
        # Trier par score combiné
        combined_predictions.sort(key=lambda x: x["combined_score"], reverse=True)
        
        result = {
            "combined_predictions": combined_predictions[:15],  # Top 15
            "lstm_available": "top_predictions" in lstm_predictions,
            "traditional_available": "overdue_attributes" in traditional_predictions,
            "combination_method": "Weighted_Average_LSTM70_Traditional30",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Combinaison terminée - {len(combined_predictions)} prédictions combinées")
        
        return result