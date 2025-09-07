@echo off
echo Demarrage du serveur backend...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause