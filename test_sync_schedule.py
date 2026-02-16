import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database.connection import SessionLocal
from app.services.session_service import SessionService

def test_sync():
    """Test the sync_session_schedule function"""
    db = SessionLocal()
    try:
        # Test with zangbeto session (ID 19)
        session_id = 19
        
        print(f"Testing sync for session {session_id}...")
        result = SessionService.sync_session_schedule(db, session_id)
        
        print("\n=== Sync Result ===")
        print(f"Message: {result.get('message')}")
        print(f"Created: {result.get('created')} new draws")
        print(f"Existing: {result.get('existing')} draws")
        print(f"Total: {result.get('total')} draws")
        
        # Verify draws were created
        from app.models.session import SessionDraw
        draws = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id
        ).order_by(SessionDraw.draw_number).all()
        
        print(f"\n=== All Draws (first 10) ===")
        for draw in draws[:10]:
            status = "Complete" if draw.is_completed else "Pending"
            print(f"  Draw #{draw.draw_number}: {draw.lottery_name} - {draw.draw_date} [{status}]")
        
        if len(draws) > 10:
            print(f"  ... and {len(draws) - 10} more draws")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_sync()
