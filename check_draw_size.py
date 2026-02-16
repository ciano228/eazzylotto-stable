
import requests

def check_draw_size():
    try:
        # Get session draws directly from API if possible, or DB
        # Using DB via python for direct access
        import psycopg2
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'katooling_main_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        cur = conn.cursor()
        
        # Get raw winning numbers to check length
        cur.execute("SELECT winning_numbers FROM session_draws WHERE session_id = 24 LIMIT 5")
        rows = cur.fetchall()
        
        print(f"📊 Analyzing Draw Sizes for Session 24:")
        for i, row in enumerate(rows):
            nums = row[0]
            print(f"   Draw {i+1}: {len(nums)} numbers ({nums})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_draw_size()
