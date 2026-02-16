import sys
import os
# Add backend directory to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database.connection import SessionLocal
from app.models.combination import Combination
from sqlalchemy import select

def check_data_formats():
    db = SessionLocal()
    try:
        # Get 5 random combinations
        combos = db.execute(select(Combination).limit(5)).scalars().all()
        
        print(f"Found {len(combos)} combinations.")
        for i, c in enumerate(combos):
            print(f"--- Combo {i+1} ---")
            print(f"Chip: '{c.chip}'")
            print(f"Ligne: '{c.ligne}'")
            print(f"Colonne: '{c.colonne}'")
            print(f"Forme: '{c.forme}'")
            print(f"Engine: '{c.engine}'")
            print(f"Beastie: '{c.beastie}'")
            print(f"Tome: '{c.tome}'")
            

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

def list_sessions():
    db = SessionLocal()
    try:
        from sqlalchemy import text
        import json
        
        print("\n--- Searching for 'zangbeto loteries' ---")
        # Search in Unified Sessions
        # Inspect columns first
        res = db.execute(text("SELECT * FROM unified_sessions WHERE name LIKE '%zangbeto%'")).fetchone()
        
        if res:
            print(f"FOUND Unified Session: {res.name} (ID: {res.id})")
            # Print keys to find schedule column
            print(f"Columns: {res._mapping.keys()}")
            
            # Try to get schedule from likely columns
            schedule_json = getattr(res, 'lottery_schedule', None) or getattr(res, 'schedule', None)
            
            if schedule_json:
                try:
                    schedule = json.loads(schedule_json) if isinstance(schedule_json, str) else schedule_json
                    print("Parsed Schedule:")
                    for i, item in enumerate(schedule):
                        print(f"  {i+1}. {item.get('name', 'Unknown')}")
                except:
                    print(f"Could not parse schedule JSON: {schedule_json}")
            else:
                print("No schedule found in likely columns.")
                
            # Also check draws for this session
            print("\n--- Checking Draws for this session ---")
            draws = db.execute(text(f"SELECT draw_date, lottery_name FROM unified_draws WHERE session_id = '{res.id}' ORDER BY draw_date ASC LIMIT 15")).fetchall()
            for i, d in enumerate(draws):
                print(f"  Draw {i+1}: {d.draw_date} - {d.lottery_name}")

        else:
            print("Session 'zangbeto loteries' not found in Unified Sessions. Checking Legacy...")
            try:
                # Check WorkSession table
                res = db.execute(text("SELECT id, name, lottery_type FROM work_sessions WHERE name LIKE '%zangbeto%'")).fetchone()
                if res:
                    print(f"FOUND Legacy Session: {res.name} (ID: {res.id})")
                    print(f"Lottery Type: {res.lottery_type}")
                    
                    # Legacy sessions usually don't have a JSON schedule but use lottery_type or global schedule
                    # Let's check draws
                    print("\n--- Checking Draws for this session ---")
                    # Legacy draws might be in 'draws' table or via 'combinations'
                    # But enabled unified system often migrates them. Let's check unified_draws with legacy ID
                    print(f"Querying unified_draws for session_uuid = '{res.id}'")
                    draws = db.execute(text(f"SELECT draw_date, lottery_name FROM unified_draws WHERE session_uuid = '{res.id}' ORDER BY draw_date ASC LIMIT 15")).fetchall()
                    if not draws:
                         print("No draws in unified_draws. Checking 'combinations' table for legacy draws...")
                         # Inspect columns first
                         try:
                             check = db.execute(text("SELECT * FROM combinations LIMIT 1")).fetchone()
                             if check:
                                 print(f"Combinations Columns: {check._mapping.keys()}")
                             
                             # Try likely names
                             date_col = 'draw_date' if 'draw_date' in check._mapping.keys() else 'date_tirage'
                             if 'date' in check._mapping.keys(): date_col = 'date'
                             
                             print(f"Using date column: {date_col}")
                             draws = db.execute(text(f"SELECT DISTINCT {date_col} as draw_date, 'Unknown' as lottery_name FROM combinations WHERE session_id = {res.id} ORDER BY {date_col} ASC LIMIT 15")).fetchall()
                         except Exception as exc:
                             print(f"Error inspecting combinations: {exc}")
                             print(f"Error inspecting combinations: {exc}")
                             db.rollback() 
                             print("Transaction rolled back. Checking 'session_draws' table (as per SessionDraw model)...")
                             
                             draws = db.execute(text(f"SELECT draw_number, cycle_position, lottery_name, draw_date FROM session_draws WHERE session_id = {res.id} ORDER BY draw_number ASC LIMIT 20")).fetchall()
                             
                             if draws:
                                 print("Found draws in session_draws:")
                                 for d in draws:
                                     print(f"  Draw #{d.draw_number} (CyclePos: {d.cycle_position}): {d.draw_date} - {d.lottery_name}")
                             else:
                                 print("No draws found in session_draws either.")

                    for i, d in enumerate(draws or []):
                        l_name = getattr(d, 'lottery_name', 'Unknown')
                        print(f"  Draw {i+1}: {d.draw_date} - {l_name}")
                else:
                    print("Session not found in Legacy either.")
            except Exception as ex:
                print(f"Legacy search error: {ex}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"Error checking sessions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data_formats()
    list_sessions()
