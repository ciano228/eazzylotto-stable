import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.database.connection import get_db
from sqlalchemy import text

def fetch_categories():
    db = next(get_db())
    try:
        print("Fetching distinct Beasties...")
        res = db.execute(text("SELECT DISTINCT beastie FROM combinations WHERE beastie IS NOT NULL")).fetchall()
        beasties = sorted([row[0] for row in res])
        print(f"FOUND {len(beasties)} BEASTIES: {beasties}")

        print("\nFetching distinct Universes...")
        res = db.execute(text("SELECT DISTINCT univers FROM combinations WHERE univers IS NOT NULL")).fetchall()
        universes = sorted([row[0] for row in res])
        print(f"FOUND {len(universes)} UNIVERSES: {universes}")
        
    finally:
        db.close()

if __name__ == "__main__":
    fetch_categories()
