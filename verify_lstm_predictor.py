
import os
import sys
import numpy as np
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

def verify_lstm():
    print("STARTING LSTM PREDICTOR PIPELINE CHECK...")
    
    # DB Connection for SQLAlchemy
    # Hardcoded for reliability in debug env
    db_url = "postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Test 1: Initialize for "engine" attribute
        print("1. Initializing LSTMPredictor for 'engine'...")
        predictor = LSTMPredictor(attribute_type='engine', universe='mundo')
        
        # Test 2: Prepare Data (The complex part)
        print("2. Running prepare_data() (Fetching Draws -> Parsing Engines)...")
        # NOTE: This requires real draws in session_draws table
        try:
            X, y, unique = predictor.prepare_data(session)
            print(f"   [SUCCESS] Data Prepared!")
            print(f"   - Input Shape (X): {X.shape}")
            print(f"   - Target Shape (y): {y.shape}")
            print(f"   - Unique Classes: {len(unique)} ({unique[:5]}...)")
            
            # Test 3: Get Recent Sequence
            print("3. Testing _get_recent_sequence()...")
            seq = predictor._get_recent_sequence(session, 10)
            print(f"   [SUCCESS] Recent Sequence: {seq}")
            
        except ValueError as ve:
            print(f"   [WARNING] Not enough data? {ve}")
        except Exception as e:
            print(f"   [ERROR] prepare_data failed: {e}")
            import traceback
            traceback.print_exc()

    finally:
        session.close()

if __name__ == "__main__":
    verify_lstm()
