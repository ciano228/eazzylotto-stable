
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.dirname(__file__))

# Import custom modules
try:
    from backend.app.ml.models.lstm_predictor import LSTMPredictor
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def train_initial_models():
    print("STARTING INITIAL MODEL TRAINING...")
    
    # DB Connection for SQLAlchemy
    db_url = "postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system"
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        attributes = ['engine', 'beastie', 'forme', 'tome']
        
        for attr in attributes:
            print(f"\nTraining model for '{attr}'...")
            try:
                predictor = LSTMPredictor(attribute_type=attr, universe='mundo')
                
                # Check if enough data
                # We know prepare_data fetches 5000 draws
                # Just call train() which calls prepare_data()
                
                results = predictor.train(session, epochs=20) # 20 epochs enough for demo
                print(f"   [SUCCESS] Accuracy: {results['final_accuracy']:.2f}")
                
            except Exception as e:
                print(f"   [ERROR] Failed to train {attr}: {e}")
                
    finally:
        session.close()

if __name__ == "__main__":
    train_initial_models()
