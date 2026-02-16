# 🔮 Activer les Prédictions LSTM

## ❌ Problème
Les prédictions LSTM affichent "Not available"

## ✅ Solution

### Étape 1: Vérifier les modèles
```bash
# Vérifier si les modèles existent
ls backend/app/ml/models/saved/
```

### Étape 2: Entraîner les modèles (si nécessaire)

Les modèles LSTM doivent être entraînés avant utilisation. Créez ce script:

**`train_lstm_models.py`**:
```python
from backend.app.ml.models.lstm_predictor import LSTMPredictor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configuration DB
db_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'Katulaa_33')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'katooling_main_system')}"

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Attributs à entraîner
attributes = ['engine', 'beastie', 'forme', 'tome']
universe = 'mundo'

for attr in attributes:
    print(f"\n🔮 Entraînement LSTM pour {attr}...")
    try:
        predictor = LSTMPredictor(attribute_type=attr, universe=universe)
        result = predictor.train(session, epochs=30)
        print(f"✅ {attr}: Précision = {result['final_accuracy']:.3f}")
    except Exception as e:
        print(f"❌ Erreur {attr}: {e}")

session.close()
print("\n✅ Entraînement terminé!")
```

### Étape 3: Exécuter l'entraînement
```bash
python train_lstm_models.py
```

**Durée**: 10-30 minutes selon les données

### Étape 4: Redémarrer le serveur
```bash
python integrated_server.py
```

## 🔧 Alternative: Désactiver temporairement

Si vous ne voulez pas entraîner les modèles maintenant, l'endpoint retournera simplement "Not available" sans erreur.

## 📊 Vérifier que ça fonctionne

Après entraînement, testez:
```bash
curl http://localhost:8881/predict/next/engine?universe=mundo
```

Devrait retourner des prédictions avec probabilités.

## ⚠️ Note

Les modèles LSTM nécessitent:
- TensorFlow installé
- Historique de tirages suffisant (>100 tirages)
- Temps d'entraînement initial

Si vous n'avez pas besoin des prédictions LSTM maintenant, vous pouvez continuer à utiliser l'application sans cette fonctionnalité.
