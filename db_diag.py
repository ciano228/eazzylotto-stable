
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_db():
    try:
        print("Checking database connection...")
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'katooling_main_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        print("Connection successful!")
        
        cursor = conn.cursor()
        
        # Check combinations count
        cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo'")
        count = cursor.fetchone()[0]
        print(f"Total combinations for 'mundo': {count}")
        
        # Check granques
        cursor.execute("SELECT DISTINCT granque_name FROM combinations WHERE univers = 'mundo' LIMIT 5")
        granques = cursor.fetchall()
        print(f"Sample granques: {granques}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
