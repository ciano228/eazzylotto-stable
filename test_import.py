import sys
import os

# Simulate integrated_server.py path setup
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    print("Attempting to import backend.app.routes.chat...")
    from backend.app.routes import chat
    print("SUCCESS: backend.app.routes.chat imported.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nAttempting to import app.services.chatbot_service...")
    from app.services.chatbot_service import ChatbotService
    print("SUCCESS: app.services.chatbot_service imported.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
