import numpy as np
import pandas as pd
import os
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib

class LSTMPredictor:
    """
    Réseau LSTM pour prédictions sophistiquées des attributs de loterie
    """
    
    def __init__(self, attribute_type: str, universe: str = "mundo"):
        self.attribute_type = attribute_type
        self.universe = universe
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = MinMaxScaler()
        self.sequence_length = 10  # Longueur des séquences pour LSTM
        self.model_path = f"backend/app/ml/models/saved/{universe}_{attribute_type}_lstm.h5"
        self.encoder_path = f"backend/app/ml/models/saved/{universe}_{attribute_type}_encoder.pkl"
        self.scaler_path = f"backend/app/ml/models/saved/{universe}_{attribute_type}_scaler.pkl"
        
        # Créer le dossier de sauvegarde s'il n'existe pas
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def prepare_data(self, db: Session) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prépare les données pour l'entraînement LSTM"""
        
        print(f"🔄 Préparation des données LSTM pour {self.attribute_type}...")
        
        # Récupérer les données historiques
        if self.attribute_type in ['forme', 'engine', 'beastie', 'tome', 'chip']:
            query = f"""
                SELECT 
                    c.{self.attribute_type} as attribute_value,
                    c.combination_id,
                    ROW_NUMBER() OVER (ORDER BY c.combination_id ASC) as sequence_order
                FROM combinations c 
                WHERE c.univers = :universe 
                AND c.{self.attribute_type} IS NOT NULL
                ORDER BY c.combination_id ASC
                LIMIT 2000
            """
        elif self.attribute_type == 'parite':
            query = """
                SELECT 
                    p.parite as attribute_value,
                    c.combination_id,
                    ROW_NUMBER() OVER (ORDER BY c.combination_id ASC) as sequence_order
                FROM combinations c 
                LEFT JOIN parite p ON c.parite_id = p.parite_id
                WHERE c.univers = :universe 
                AND p.parite IS NOT NULL
                ORDER BY c.combination_id ASC
                LIMIT 2000
            """
        elif self.attribute_type == 'unidos':
            query = """
                SELECT 
                    u.unidos as attribute_value,
                    c.combination_id,
                    ROW_NUMBER() OVER (ORDER BY c.combination_id ASC) as sequence_order
                FROM combinations c 
                LEFT JOIN unidos u ON c.unidos_id = u.unidos_id
                WHERE c.univers = :universe 
                AND u.unidos IS NOT NULL
                ORDER BY c.combination_id ASC
                LIMIT 2000
            """
        
        result = db.execute(text(query), {"universe": self.universe})
        data = result.fetchall()
        
        if len(data) < self.sequence_length + 10:
            raise ValueError(f"Pas assez de données pour {self.attribute_type} (minimum {self.sequence_length + 10})")
        
        # Convertir en DataFrame
        df = pd.DataFrame(data, columns=['attribute_value', 'combination_id', 'sequence_order'])
        
        # Encoder les valeurs catégorielles
        values = df['attribute_value'].values
        unique_values = list(set(values))
        
        # Encoder les valeurs
        encoded_values = self.label_encoder.fit_transform(values)
        
        # Créer des séquences pour LSTM
        X, y = self._create_sequences(encoded_values)
        
        print(f"✅ Données préparées: {len(X)} séquences de longueur {self.sequence_length}")
        print(f"📊 Valeurs uniques: {len(unique_values)} - {unique_values}")
        
        return X, y, unique_values
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crée des séquences temporelles pour LSTM"""
        
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            # Séquence d'entrée (10 valeurs précédentes)
            X.append(data[i:(i + self.sequence_length)])
            # Valeur à prédire (valeur suivante)
            y.append(data[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def build_model(self, num_classes: int) -> Sequential:
        """Construit le modèle LSTM"""
        
        print(f"🏗️ Construction du modèle LSTM pour {num_classes} classes...")
        
        model = Sequential([
            # Couche d'embedding pour les valeurs catégorielles
            Embedding(input_dim=num_classes, output_dim=50, input_length=self.sequence_length),
            
            # Première couche LSTM avec dropout
            LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),
            
            # Deuxième couche LSTM
            LSTM(64, dropout=0.2, recurrent_dropout=0.2),
            
            # Couches denses avec dropout
            Dense(50, activation='relu'),
            Dropout(0.3),
            Dense(25, activation='relu'),
            Dropout(0.2),
            
            # Couche de sortie (classification)
            Dense(num_classes, activation='softmax')
        ])
        
        # Compiler le modèle
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Modèle LSTM construit avec succès!")
        return model
    
    def train(self, db: Session, epochs: int = 50, validation_split: float = 0.2) -> Dict[str, Any]:
        """Entraîne le modèle LSTM"""
        
        print(f"🚀 Début de l'entraînement LSTM pour {self.attribute_type}...")
        
        try:
            # Préparer les données
            X, y, unique_values = self.prepare_data(db)
            
            # Construire le modèle
            self.model = self.build_model(len(unique_values))
            
            # Entraîner le modèle
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=32,
                validation_split=validation_split,
                verbose=1,
                shuffle=True
            )
            
            # Sauvegarder le modèle et les encodeurs
            self.save_model()
            
            # Calculer les métriques finales
            final_loss = history.history['loss'][-1]
            final_accuracy = history.history['accuracy'][-1]
            val_loss = history.history['val_loss'][-1] if 'val_loss' in history.history else None
            val_accuracy = history.history['val_accuracy'][-1] if 'val_accuracy' in history.history else None
            
            training_results = {
                "attribute_type": self.attribute_type,
                "universe": self.universe,
                "epochs_trained": epochs,
                "final_loss": float(final_loss),
                "final_accuracy": float(final_accuracy),
                "validation_loss": float(val_loss) if val_loss else None,
                "validation_accuracy": float(val_accuracy) if val_accuracy else None,
                "unique_values": unique_values,
                "training_samples": len(X),
                "sequence_length": self.sequence_length,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Entraînement terminé!")
            print(f"📊 Précision finale: {final_accuracy:.3f}")
            print(f"📊 Précision validation: {val_accuracy:.3f}" if val_accuracy else "")
            
            return training_results
            
        except Exception as e:
            print(f"❌ Erreur lors de l'entraînement: {e}")
            raise e
    
    def predict_next(self, db: Session, sequence_length: int = None) -> Dict[str, Any]:
        """Prédit la prochaine valeur avec LSTM"""
        
        if sequence_length is None:
            sequence_length = self.sequence_length
        
        print(f"🔮 Prédiction LSTM pour {self.attribute_type}...")
        
        try:
            # Charger le modèle si nécessaire
            if self.model is None:
                self.load_model()
            
            # Récupérer la séquence récente
            recent_sequence = self._get_recent_sequence(db, sequence_length)
            
            if len(recent_sequence) < sequence_length:
                raise ValueError(f"Pas assez de données récentes ({len(recent_sequence)} < {sequence_length})")
            
            # Encoder la séquence
            encoded_sequence = self.label_encoder.transform(recent_sequence)
            
            # Préparer pour la prédiction
            X_pred = np.array([encoded_sequence])
            
            # Faire la prédiction
            predictions = self.model.predict(X_pred, verbose=0)
            predicted_probs = predictions[0]
            
            # Décoder les prédictions
            predicted_classes = np.argsort(predicted_probs)[::-1]  # Trier par probabilité décroissante
            
            results = []
            for i, class_idx in enumerate(predicted_classes[:5]):  # Top 5
                try:
                    predicted_value = self.label_encoder.inverse_transform([class_idx])[0]
                    confidence = float(predicted_probs[class_idx])
                    
                    results.append({
                        "rank": i + 1,
                        "predicted_value": predicted_value,
                        "confidence": confidence,
                        "confidence_percent": round(confidence * 100, 1)
                    })
                except:
                    continue
            
            prediction_result = {
                "attribute_type": self.attribute_type,
                "universe": self.universe,
                "predictions": results,
                "model_type": "LSTM",
                "sequence_used": recent_sequence.tolist(),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Prédiction LSTM terminée - Top prédiction: {results[0]['predicted_value']} ({results[0]['confidence_percent']}%)")
            
            return prediction_result
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction LSTM: {e}")
            raise e
    
    def _get_recent_sequence(self, db: Session, length: int) -> np.ndarray:
        """Récupère la séquence récente pour la prédiction"""
        
        if self.attribute_type in ['forme', 'engine', 'beastie', 'tome', 'chip']:
            query = f"""
                SELECT c.{self.attribute_type} as attribute_value
                FROM combinations c 
                WHERE c.univers = :universe 
                AND c.{self.attribute_type} IS NOT NULL
                ORDER BY c.combination_id DESC
                LIMIT :length
            """
        elif self.attribute_type == 'parite':
            query = """
                SELECT p.parite as attribute_value
                FROM combinations c 
                LEFT JOIN parite p ON c.parite_id = p.parite_id
                WHERE c.univers = :universe 
                AND p.parite IS NOT NULL
                ORDER BY c.combination_id DESC
                LIMIT :length
            """
        elif self.attribute_type == 'unidos':
            query = """
                SELECT u.unidos as attribute_value
                FROM combinations c 
                LEFT JOIN unidos u ON c.unidos_id = u.unidos_id
                WHERE c.univers = :universe 
                AND u.unidos IS NOT NULL
                ORDER BY c.combination_id DESC
                LIMIT :length
            """
        
        result = db.execute(text(query), {"universe": self.universe, "length": length})
        data = result.fetchall()
        
        # Inverser l'ordre pour avoir la séquence chronologique
        sequence = np.array([row[0] for row in reversed(data)])
        
        return sequence
    
    def save_model(self):
        """Sauvegarde le modèle et les encodeurs"""
        
        if self.model is not None:
            self.model.save(self.model_path)
            joblib.dump(self.label_encoder, self.encoder_path)
            print(f"💾 Modèle sauvegardé: {self.model_path}")
    
    def load_model(self):
        """Charge le modèle et les encodeurs"""
        
        if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
            self.model = load_model(self.model_path)
            self.label_encoder = joblib.load(self.encoder_path)
            print(f"📂 Modèle chargé: {self.model_path}")
        else:
            raise FileNotFoundError(f"Modèle non trouvé pour {self.attribute_type}")
    
    def evaluate_model(self, db: Session) -> Dict[str, Any]:
        """Évalue la performance du modèle"""
        
        try:
            # Préparer les données de test
            X, y, unique_values = self.prepare_data(db)
            
            # Charger le modèle
            if self.model is None:
                self.load_model()
            
            # Évaluer
            loss, accuracy = self.model.evaluate(X, y, verbose=0)
            
            evaluation_results = {
                "attribute_type": self.attribute_type,
                "universe": self.universe,
                "test_loss": float(loss),
                "test_accuracy": float(accuracy),
                "test_samples": len(X),
                "unique_classes": len(unique_values),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"📊 Évaluation {self.attribute_type}: Précision = {accuracy:.3f}")
            
            return evaluation_results
            
        except Exception as e:
            print(f"❌ Erreur lors de l'évaluation: {e}")
            return {"error": str(e)}