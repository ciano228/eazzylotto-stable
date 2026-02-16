import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database.connection import SessionLocal
from app.services.advanced_statistics_service import AdvancedStatisticsService

def test_session_stats(session_id, universe='mundo'):
    db = SessionLocal()
    try:
        print(f"\n--- Testing Stats for Session {session_id} (Universe: {universe}) ---")
        
        # Check if session exists first (Unified or Legacy)
        from app.models.session import WorkSession
        from sqlalchemy import text
        
        is_unified = isinstance(session_id, str) and len(str(session_id)) > 8
        exists = False
        
        if is_unified:
             res = db.execute(text("SELECT id FROM unified_sessions WHERE uuid = :u"), {"u": session_id}).first()
             if res: exists = True
        else:
             res = db.query(WorkSession).filter(WorkSession.id == session_id).first()
             if res: exists = True
             
        if not exists:
            # Try to see if it's a unified numeric ID for testing
            if isinstance(session_id, int):
                 res = db.execute(text("SELECT uuid FROM unified_sessions WHERE id = :id"), {"id": session_id}).first()
                 if res:
                     print(f"Found Unified Session via ID {session_id}, UUID is {res.uuid}")
                     session_id = res.uuid
                     exists = True

        if not exists:
            print(f"Session {session_id} not found.")
            return

        stats = AdvancedStatisticsService.calculate_session_overdue_stats(
            session_id=session_id,
            universe=universe,
            db=db
        )
        
        print(f"Total Draws: {stats.get('total_draws')}")
        attributes = stats.get('attributes', [])
        print(f"Total Attributes Calculated: {len(attributes)}")
        
        if attributes:
            print("\nTop 5 Overdue Attributes:")
            for attr in attributes[:5]:
                 print(f" - {attr['type']} {attr['value']}: Score={attr['score']}, Gap={attr['gap']}")
            
            print("\nSample Chips Stats:")
            chips = [a for a in attributes if a['type'] == 'chip'][:5]
            for c in chips:
                print(f" - {c['value']}: Gap={c['gap']}")
        else:
            print("No attributes found.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Test with Legacy Session 24 (Sim_2024_Mon-Sun_weekly)
    test_session_stats(24)
