import uvicorn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from main import app

if __name__ == "__main__":
    print("Demarrage serveur EazzyCalculator...")
    print("API: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)