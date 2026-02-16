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
from session_statistics_engine import SessionStatisticsEngine
import itertools

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
        """Prépare les données TEMPRAILES REELLES pour l'entraînement LSTM"""
        print(f"Preparation des donnees Sequentielles pour {self.attribute_type}...")

        # 1. Fetch Session Draws (All History)
        # We need a way to get all draws. Since we don't have session_id here, 
        # we might need to query the session_draws table directly.
        # Let's assume we want ALL draws from ALL sessions for the universe (or just filter by universe if stored).
        # Typically draws are per session. Let's fetch draws from session 2 (Main) or all.
        # For now, let's grab all draws from table `session_draws` ordered by date.
        
        query = text("""
            SELECT winning_numbers, draw_date 
            FROM session_draws 
            ORDER BY draw_date ASC, draw_number ASC
            LIMIT 5000
        """)
        result = db.execute(query)
        draws_rows = result.fetchall()
        
        if not draws_rows:
            raise ValueError("Aucun tirage trouvé dans l'historique.")

        # 2. Extract Attributes using Engine Logic
        # We need the map.
        # Config DB manually or from env
        import os
        db_config = {
            'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        stats_engine = SessionStatisticsEngine(db_config)
        universe_map = stats_engine._load_universe_map(self.universe)
        
        raw_sequence = []
        
        for row in draws_rows:
            nums = row[0] # winning_numbers
            if not nums or len(nums) < 2: continue
            
            # clean nums
            valid_nums = [int(n) for n in nums if str(n).isdigit()]
            
            # Generate pairs
            pairs = list(itertools.combinations(valid_nums, 2))
            
            draw_attrs = []
            for p in pairs:
                p_key = tuple(sorted(p))
                if p_key in universe_map:
                    attrs_list = universe_map[p_key]
                    for a in attrs_list:
                        val = a.get(self.attribute_type)
                        # Specific handling for base_name or others
                        target_key = self.attribute_type
                        if target_key == 'granque': target_key = 'granque_name'
                        
                        val = a.get(target_key)
                        if val and val != "---":
                            draw_attrs.append(val)
            
            # Add to main sequence
            # Strategy: Flatten? Or take most frequent?
            # Flattening preserves all data.
            raw_sequence.extend(draw_attrs)

        if len(raw_sequence) < self.sequence_length + 10:
             raise ValueError(f"Pas assez de données d'attributs ({len(raw_sequence)}) pour l'entraînement.")

        # 3. Encode
        values = np.array(raw_sequence)
        unique_values = list(set(values))
        encoded_values = self.label_encoder.fit_transform(values)
        
        # 4. Create Sequences
        X, y = self._create_sequences(encoded_values)
        
        print(f"Donnees Sequentielles pretes: {len(X)} sequences.")
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
        
        print(f"Construction du modele LSTM pour {num_classes} classes...")
        
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
        
        print("Modele LSTM construit avec succes!")
        return model
    
    def train(self, db: Session, epochs: int = 50, validation_split: float = 0.2) -> Dict[str, Any]:
        """Entraîne le modèle LSTM"""
        
        print(f"Debut de l'entrainement LSTM pour {self.attribute_type}...")
        
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
            
            print(f"Entrainement termine!")
            print(f"Precision finale: {final_accuracy:.3f}")
            print(f"Precision validation: {val_accuracy:.3f}" if val_accuracy else "")
            
            return training_results
            
        except Exception as e:
            print(f"Erreur lors de l'entrainement: {e}")
            raise e
    
    def predict_next(self, db: Session, sequence_length: int = None) -> Dict[str, Any]:
        """Prédit la prochaine valeur avec LSTM"""
        
        if sequence_length is None:
            sequence_length = self.sequence_length
        
        print(f"Prediction LSTM pour {self.attribute_type}...")
        
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
            
            print(f"SUCCESS: Prediction LSTM terminee - Top prediction: {results[0]['predicted_value']} ({results[0]['confidence_percent']}%)")
            
            return prediction_result
            
        except Exception as e:
            print(f"ERROR: Erreur lors de la prediction LSTM: {e}")
            raise e
    
    def _get_recent_sequence(self, db: Session, length: int) -> np.ndarray:
        """Récupère la séquence RÉCENTE pour la prédiction (Live)"""
        
        # Fetch last N draws
        query = text("""
            SELECT winning_numbers 
            FROM session_draws 
            ORDER BY draw_date DESC, draw_number DESC
            LIMIT 50
        """)
        result = db.execute(query)
        rows = result.fetchall()
        
        # Setup Engine
        import os
        db_config = {
            'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        stats_engine = SessionStatisticsEngine(db_config)
        universe_map = stats_engine._load_universe_map(self.universe)
        
        raw_sequence = []
        
        # Process in REVERSE to build chronological history (Older -> Newer)
        # rows are DESC (Newest first).
        for row in reversed(rows):
            nums = row[0]
            if not nums or len(nums) < 2: continue
            valid_nums = [int(n) for n in nums if str(n).isdigit()]
            pairs = list(itertools.combinations(valid_nums, 2))
            
            for p in pairs:
                p_key = tuple(sorted(p))
                if p_key in universe_map:
                    attrs_list = universe_map[p_key]
                    for a in attrs_list:
                        target_key = self.attribute_type
                        if target_key == 'granque': target_key = 'granque_name'
                        val = a.get(target_key)
                        if val and val != "---":
                            raw_sequence.append(val)
                            
        # We need the LAST 'length' items
        if len(raw_sequence) < length:
             return np.array(raw_sequence) # Short sequence
             
        return np.array(raw_sequence[-length:])
    
    def save_model(self):
        """Sauvegarde le modèle et les encodeurs"""
        
        if self.model is not None:
            self.model.save(self.model_path)
            joblib.dump(self.label_encoder, self.encoder_path)
            print(f"Modele sauvegarde: {self.model_path}")
    
    def load_model(self):
        """Charge le modèle et les encodeurs"""
        
        if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
            self.model = load_model(self.model_path)
            self.label_encoder = joblib.load(self.encoder_path)
            print(f"Modele charge: {self.model_path}")
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
            
            print(f"Evaluation {self.attribute_type}: Precision = {accuracy:.3f}")
            
            return evaluation_results
            
        except Exception as e:
            print(f"❌ Erreur lors de l'évaluation: {e}")
            return {"error": str(e)}