@echo off
REM Script de test rapide pour l'implementation des drawers
REM EazzyCalculator v2.0.2

echo ========================================
echo TEST IMPLEMENTATION DRAWERS
echo ========================================
echo.

echo [1/5] Test endpoint structure drawers fruity...
curl -s "http://localhost:8881/analytics/chip-drawers-structure/fruity" > test_drawer_structure.json
if %ERRORLEVEL% EQU 0 (
    echo [OK] Endpoint structure drawers accessible
    type test_drawer_structure.json | findstr "total_drawers"
) else (
    echo [ERREUR] Endpoint structure drawers inaccessible
)
echo.

echo [2/5] Test endpoint temporal drawer data...
curl -s "http://localhost:8881/analytics/temporal-drawer-data?universe=fruity&date_start=2024-01-01&date_end=2024-12-31&marking_type=drawer" > test_temporal_drawer.json
if %ERRORLEVEL% EQU 0 (
    echo [OK] Endpoint temporal drawer data accessible
    type test_temporal_drawer.json | findstr "drawer_details"
) else (
    echo [ERREUR] Endpoint temporal drawer data inaccessible
)
echo.

echo [3/5] Test chip44 fruity (cas multiple denominations)...
curl -s "http://localhost:8881/api/formes/real/fruity/chip/chip44" > test_chip44.json
if %ERRORLEVEL% EQU 0 (
    echo [OK] Endpoint chip44 accessible
    type test_chip44.json | findstr "bed 1/bed 8"
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Denominations multiples correctement groupees
    ) else (
        echo [ATTENTION] Denominations multiples non groupees
    )
) else (
    echo [ERREUR] Endpoint chip44 inaccessible
)
echo.

echo [4/5] Verification base de donnees drawers...
python -c "import psycopg2; conn=psycopg2.connect(host='localhost',database='katooling_main_system',user='postgres',password='Katulaa_33'); cur=conn.cursor(); cur.execute('SELECT COUNT(DISTINCT drawer) FROM combinations WHERE drawer IS NOT NULL'); print(f'[OK] Drawers uniques en BD: {cur.fetchone()[0]}'); conn.close()" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible de verifier la BD
)
echo.

echo [5/5] Test frontend katula-temporal-analysis.html...
if exist "frontend\katula-temporal-analysis.html" (
    findstr /I "drawer" frontend\katula-temporal-analysis.html >nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Frontend contient support drawers
    ) else (
        echo [ATTENTION] Frontend ne contient pas support drawers
    )
) else (
    echo [ERREUR] Fichier katula-temporal-analysis.html introuvable
)
echo.

echo ========================================
echo RESUME DES TESTS
echo ========================================
echo.
echo Fichiers de test generes:
echo - test_drawer_structure.json
echo - test_temporal_drawer.json
echo - test_chip44.json
echo.
echo Consultez RAPPORT_DRAWERS_IMPLEMENTATION.md pour details complets
echo.
pause
