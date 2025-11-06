#!/usr/bin/env python3
"""
Script pour consolider la structure EazzyCalculator
Utilise eazzylotto-final/ comme base principale
"""
import os
import shutil
from pathlib import Path

def consolider_structure():
    """Consolider toute la structure dans une organisation claire"""
    
    base_dir = Path("c:/Users/User/eazzycalculator")
    source_dir = base_dir / "eazzylotto-final"
    target_dir = base_dir / "app"
    
    print("=== CONSOLIDATION STRUCTURE EAZZYCALCULATOR ===\n")
    
    # 1. Créer la nouvelle structure
    print("1. Création de la nouvelle structure...")
    
    structure = {
        "app": {
            "pages": {
                "dashboard": [],
                "katula": [],
                "sessions": [],
                "tools": [],
                "auth": []
            },
            "assets": {
                "css": [],
                "js": [],
                "images": []
            },
            "api": [],  # Lien vers backend/
            "docs": []
        }
    }
    
    # Créer les dossiers
    for main_folder, sub_folders in structure.items():
        main_path = base_dir / main_folder
        main_path.mkdir(exist_ok=True)
        
        if isinstance(sub_folders, dict):
            for sub_folder, _ in sub_folders.items():
                sub_path = main_path / sub_folder
                sub_path.mkdir(exist_ok=True)
                
                if sub_folder == "pages":
                    for page_type in sub_folders[sub_folder]:
                        page_path = sub_path / page_type
                        page_path.mkdir(exist_ok=True)
    
    print("   [OK] Structure créée")
    
    # 2. Mapper les pages par catégorie
    print("\n2. Classification des pages...")
    
    page_mapping = {
        "dashboard": [
            "dashboard.html", "dashboard-simple.html", "dashboard-react-test.html"
        ],
        "katula": [
            "katula-dynamic.html", "katula-table.html", "katula-temporal-analysis.html",
            "katula-enhanced.html", "katula-forme-layout.html", "katula-fruity-exact.html",
            "katula-fruity-icons.html", "katula-icons.html", "katula-multi-universe.html",
            "katula-subdivided.html"
        ],
        "sessions": [
            "session-diagnostic.html", "test-sessions.html", "test-sessions-data.html",
            "test-sessions-simple.html", "test-session-complete.html"
        ],
        "tools": [
            "smart-input.html", "smart-input-complete.html", "smart-input-debug.html",
            "combination-generator.html", "pattern-viewer.html", "prediction-panel.html",
            "gap-analysis.html", "intelligent-alerts.html", "results-history.html"
        ],
        "auth": [
            "login.html", "signup.html", "parametres.html"
        ]
    }
    
    # 3. Copier les pages depuis eazzylotto-final
    print("\n3. Copie des pages principales...")
    
    if source_dir.exists():
        for category, pages in page_mapping.items():
            target_category = base_dir / "app" / "pages" / category
            
            for page in pages:
                source_file = source_dir / page
                if source_file.exists():
                    target_file = target_category / page
                    shutil.copy2(source_file, target_file)
                    print(f"   [OK] {page} -> {category}/")
                else:
                    print(f"   [SKIP] {page} (non trouvé)")
    
    # 4. Copier les assets
    print("\n4. Copie des assets...")
    
    assets_mapping = {
        "css": ["*.css"],
        "js": ["*.js"],
        "images": ["*.png", "*.jpg", "*.svg", "*.ico"]
    }
    
    source_assets = source_dir / "assets"
    if source_assets.exists():
        for asset_type, patterns in assets_mapping.items():
            source_asset_dir = source_assets / asset_type
            target_asset_dir = base_dir / "app" / "assets" / asset_type
            
            if source_asset_dir.exists():
                for file_path in source_asset_dir.rglob("*"):
                    if file_path.is_file():
                        target_file = target_asset_dir / file_path.name
                        shutil.copy2(file_path, target_file)
                        print(f"   [OK] {file_path.name} -> assets/{asset_type}/")
    
    # 5. Créer un index.html principal
    print("\n5. Création de l'index principal...")
    
    index_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EazzyCalculator - Accueil</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        .header {
            margin-bottom: 50px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 50px 0;
        }
        .category-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .category-card h3 {
            color: #ffd700;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        .page-link {
            display: block;
            padding: 10px 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .page-link:hover {
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 EazzyCalculator</h1>
            <p>Système unifié d'analyse et de prédiction</p>
        </div>
        
        <div class="categories">
            <div class="category-card">
                <h3>📊 Dashboard</h3>
                <a href="pages/dashboard/dashboard.html" class="page-link">Dashboard Principal</a>
                <a href="pages/dashboard/dashboard-simple.html" class="page-link">Dashboard Simple</a>
            </div>
            
            <div class="category-card">
                <h3>🎯 Katula</h3>
                <a href="pages/katula/katula-dynamic.html" class="page-link">Katula Dynamique</a>
                <a href="pages/katula/katula-table.html" class="page-link">Table de Katula</a>
                <a href="pages/katula/katula-temporal-analysis.html" class="page-link">Analyse Temporelle</a>
                <a href="pages/katula/katula-multi-universe.html" class="page-link">Multi-Univers</a>
            </div>
            
            <div class="category-card">
                <h3>🔧 Outils</h3>
                <a href="pages/tools/smart-input.html" class="page-link">Smart Input</a>
                <a href="pages/tools/combination-generator.html" class="page-link">Générateur</a>
                <a href="pages/tools/pattern-viewer.html" class="page-link">Patterns</a>
                <a href="pages/tools/prediction-panel.html" class="page-link">Prédictions</a>
            </div>
            
            <div class="category-card">
                <h3>📋 Sessions</h3>
                <a href="pages/sessions/session-diagnostic.html" class="page-link">Diagnostic</a>
                <a href="pages/sessions/test-sessions-data.html" class="page-link">Test Sessions</a>
            </div>
            
            <div class="category-card">
                <h3>🔐 Authentification</h3>
                <a href="pages/auth/login.html" class="page-link">Connexion</a>
                <a href="pages/auth/signup.html" class="page-link">Inscription</a>
                <a href="pages/auth/parametres.html" class="page-link">Paramètres</a>
            </div>
            
            <div class="category-card">
                <h3>🧪 Tests</h3>
                <a href="test-nouvelles-colonnes.html" class="page-link">Test Nouvelles Colonnes</a>
                <a href="pages/tools/gap-analysis.html" class="page-link">Analyse des Écarts</a>
            </div>
        </div>
        
        <div style="margin-top: 50px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
            <h3>🚀 Démarrage Rapide</h3>
            <p>1. Backend: <code>cd backend && python main.py</code></p>
            <p>2. Frontend: <code>python -m http.server 8080</code></p>
            <p>3. Accès: <a href="http://localhost:8080" style="color: #ffd700;">http://localhost:8080</a></p>
        </div>
    </div>
</body>
</html>"""
    
    index_file = base_dir / "app" / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("   [OK] Index principal créé")
    
    # 6. Créer un script de démarrage unifié
    print("\n6. Script de démarrage unifié...")
    
    start_script = """@echo off
echo === DEMARRAGE EAZZYCALCULATOR ===
echo.

echo 1. Demarrage du backend...
start "Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo 2. Demarrage du frontend...
start "Frontend" cmd /k "cd app && python -m http.server 8080"

timeout /t 2 /nobreak > nul

echo 3. Ouverture du navigateur...
start http://localhost:8080

echo.
echo === SYSTEME DEMARRE ===
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8080
echo.
pause"""
    
    start_file = base_dir / "demarrer_eazzycalculator.bat"
    with open(start_file, 'w', encoding='utf-8') as f:
        f.write(start_script)
    
    print("   [OK] Script de démarrage créé")
    
    # 7. Résumé
    print("\n=== CONSOLIDATION TERMINÉE ===")
    print(f"Structure unifiée créée dans: {base_dir / 'app'}")
    print("\nNouvelle organisation:")
    print("📁 app/")
    print("  📁 pages/")
    print("    📁 dashboard/    - Tableaux de bord")
    print("    📁 katula/       - Analyses Katula")
    print("    📁 sessions/     - Gestion sessions")
    print("    📁 tools/        - Outils divers")
    print("    📁 auth/         - Authentification")
    print("  📁 assets/")
    print("    📁 css/          - Styles")
    print("    📁 js/           - Scripts")
    print("    📁 images/       - Images")
    print("  📄 index.html      - Page d'accueil")
    print("\n🚀 Pour démarrer: double-cliquez sur 'demarrer_eazzycalculator.bat'")

if __name__ == "__main__":
    consolider_structure()