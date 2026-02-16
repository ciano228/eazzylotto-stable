
import os
import sys
from sqlalchemy.orm import Session
from backend.app.ml.models.lstm_predictor import LSTMPredictor
from backend.database.connection import get_db
import traceback

# Setup DB session
db_gen = get_db()
db = next(db_gen)

def test_prediction(attr):
    print(f"\n--- Testing Prediction for {attr} ---")
    try:
        predictor = LSTMPredictor(attribute_type=attr, universe='mundo')
        if not os.path.exists(predictor.model_path):
            print(f"Model file missing: {predictor.model_path}")
            return
            
        print(f"Model found at {predictor.model_path}")
        result = predictor.predict_next(db)
        print("Success!")
        print(result)
    except Exception as e:
        print("FAILED!")
        traceback.print_exc()

if __name__ == "__main__":
    test_prediction('forme')
    test_prediction('engine')
