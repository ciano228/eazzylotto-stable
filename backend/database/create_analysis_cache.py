import psycopg2
import sys

def create_cache_table():
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔄 Creating session_draw_analyses table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_draw_analyses (
                id SERIAL PRIMARY KEY,
                session_draw_id INTEGER NOT NULL REFERENCES session_draws(id) ON DELETE CASCADE,
                universe VARCHAR(50) NOT NULL,
                analysis_results JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_draw_id, universe)
            );
            
            -- Addition of an index for performance
            CREATE INDEX IF NOT EXISTS idx_session_draw_analyses_composite 
            ON session_draw_analyses(session_draw_id, universe);
        """)
        
        conn.commit()
        print("✅ table session_draw_analyses created successfully!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    if create_cache_table():
        sys.exit(0)
    else:
        sys.exit(1)
