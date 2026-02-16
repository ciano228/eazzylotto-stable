import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.database.connection import engine

def check_pairs():
    pairs_to_check = [
        (6, 80), 
        (12, 27),
        (82, 86) # This one works
    ]
    
    universe = "mundo"
    
    with engine.connect() as connection:
        for n1, n2 in pairs_to_check:
            # Check direct
            print(f"Checking {n1}-{n2}...")
            query = text("""
                SELECT combination_id, combination, univers 
                FROM combinations 
                WHERE num1 = :n1 AND num2 = :n2 AND univers = :u
            """)
            result = connection.execute(query, {"n1": n1, "n2": n2, "u": universe}).fetchone()
            
            if result:
                print(f"  FOUND: {result}")
            else:
                print(f"  NOT FOUND")

            # Check reverse just in case
            print(f"Checking reversed {n2}-{n1}...")
            result_rev = connection.execute(query, {"n1": n2, "n2": n1, "u": universe}).fetchone()
            if result_rev:
                print(f"  FOUND REVERSE: {result_rev}")
            else:
                print(f"  NOT FOUND REVERSE")

if __name__ == "__main__":
    check_pairs()
