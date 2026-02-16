import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database.connection import SessionLocal
from sqlalchemy import text
from datetime import timedelta

def fix_periodicity():
    db = SessionLocal()
    try:
        session_id = 19
        print(f"Fixing periodicity for Session {session_id} (zangbeto loteries)...")

        # 1. Fetch Session Start Date
        start_date_res = db.execute(text(f"SELECT start_date, cycle_length FROM work_sessions WHERE id = {session_id}")).fetchone()
        if not start_date_res:
            print("Session not found!")
            return
        
        start_date = start_date_res.start_date
        cycle_length = start_date_res.cycle_length or 7
        print(f"Start Date: {start_date}, Cycle Length: {cycle_length}")

        # 2. Fetch all draws sorted by date
        draws = db.execute(text(f"SELECT id, draw_date, lottery_name FROM session_draws WHERE session_id = {session_id} ORDER BY draw_date ASC")).fetchall()
        
        print(f"Found {len(draws)} draws. Re-calculating positions...")
        
        updates = []
        for d in draws:
            # Calculate Day Index (1-based)
            delta_days = (d.draw_date - start_date).days
            # Assuming 1 draw per day for simplicity, or just map date to slot
            # If start_date is Monday, delta=0 is Mon.
            
            new_draw_number = delta_days + 1
            new_cycle_pos = delta_days % cycle_length
            
            print(f"Draw {d.lottery_name} ({d.draw_date}): Delta={delta_days} => Num={new_draw_number}, Pos={new_cycle_pos}")
            
            updates.append({
                "id": d.id,
                "draw_number": new_draw_number,
                "cycle_position": new_cycle_pos
            })
            
        # 3. Apply updates
        print(f"Applying {len(updates)} updates...")
        for u in updates:
            db.execute(text(f"UPDATE session_draws SET draw_number = :draw_number, cycle_position = :cycle_position WHERE id = :id"), u)
            
        db.commit()
        print("Periodicity fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_periodicity()
