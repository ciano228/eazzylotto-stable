import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.database.connection import engine

def inspect_prediction_records():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'prediction_records'"))
        columns = [(row[0], row[1]) for row in result]
        for col in columns:
            print(f"Column: {col[0]}, Type: {col[1]}")

if __name__ == "__main__":
    inspect_prediction_records()
