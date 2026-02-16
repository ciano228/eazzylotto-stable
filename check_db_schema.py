
import os
import psycopg2
from backend.unified_db_session_service import UnifiedDBSessionService

service = UnifiedDBSessionService()
config = service.db_config

try:
    conn = psycopg2.connect(**config)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations'")
    columns = [row[0] for row in cur.fetchall()]
    print("Columns in 'combinations' table:", columns)
    
    # Also check if any data exists for 'mundo'
    cur.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo'")
    count = cur.fetchone()[0]
    print(f"Rows for 'mundo': {count}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
