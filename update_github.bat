@echo off
REM Script de mise à jour GitHub pour EazzyCalculator v2.0.5
REM Usage: update_github.bat

echo ==========================================
echo   MISE A JOUR GITHUB - EazzyCalculator
echo   Version 2.0.5
echo ==========================================
echo.

REM Vérifier si on est dans le bon répertoire
if not exist "integrated_server.py" (
    echo [ERREUR] Executer depuis la racine du projet
    pause
    exit /b 1
)

echo [1/5] Verification de l'etat Git...
git status
echo.

set /p confirm="Continuer avec le commit? (o/n): "
if /i not "%confirm%"=="o" (
    echo [ANNULE] par l'utilisateur
    pause
    exit /b 1
)

echo.
echo [2/5] Ajout des fichiers modifies...
git add integrated_server.py
git add frontend/assets/js/katula-dynamic.js
git add frontend/katula-dynamic.html
git add ETAT_APPLICATION_2025.md
git add README.md
git add update_github.bat
git add update_github.sh

echo.
echo [OK] Fichiers ajoutes
git status

echo.
echo [3/5] Commit des changements...
git commit -m "v2.0.5: Denominations multiples + UX univers selectionne" -m "" -m "Support complet denominations avec slash (rainbow 6/rainbow 9)" -m "Endpoint /api/formes/real/{universe}/all corrige" -m "Bandeau colore avec icones dynamiques par univers" -m "Attenuation chips non selectionnes" -m "Surbrillance chip actif avec bordure bleue" -m "Affichage nombre de formes par univers" -m "" -m "Fichiers modifies:" -m "- integrated_server.py (endpoint formes/all)" -m "- katula-dynamic.js (v11: API adapter + UX)" -m "- katula-dynamic.html (version script v=11)" -m "- ETAT_APPLICATION_2025.md (documentation complete)"

echo.
echo [4/5] Push vers GitHub...
git push origin main

echo.
echo [5/5] Creation du tag v2.0.5...
git tag -a v2.0.5 -m "Version 2.0.5 - Denominations multiples + UX amelioree"
git push origin v2.0.5

echo.
echo ==========================================
echo   [OK] MISE A JOUR GITHUB TERMINEE
echo ==========================================
echo.
echo Prochaines etapes:
echo 1. Verifier sur GitHub que tous les fichiers sont presents
echo 2. Creer une Release sur GitHub (optionnel)
echo 3. Mettre a jour la documentation si necessaire
echo.
echo Version 2.0.5 publiee avec succes!
echo.
pause
