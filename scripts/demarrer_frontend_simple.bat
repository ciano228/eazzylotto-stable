@echo off
echo Demarrage du serveur frontend...
cd frontend
python -m http.server 8080
pause