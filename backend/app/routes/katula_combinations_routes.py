"""
Routes pour la Table de Katula basée sur 'combinations'
API endpoints utilisant la vraie logique métier
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.database.database_postgresql import get_db
from backend.app.services.katula_combinations_service import KatulaCombinationsService

router = APIRouter(prefix="/api/katula-real", tags=["katula-real"])

@router.get("/health")
async def health_check():
    """Vérification de santé du service Katula réel"""
    return {
        "status": "healthy",
        "service": "katula-combinations",
        "version": "1.0.0",
        "data_source": "combinations_table"
    }

@router.get("/{universe}")
async def get_real_katula_table(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère la vraie table de Katula depuis la table 'combinations'
    Logique métier originale : chip + forme + denomination
    """
    try:
        table_data = KatulaCombinationsService.get_katula_table_from_combinations(db, universe)
        
        if "error" in table_data:
            raise HTTPException(status_code=500, detail=table_data["error"])
        
        return {
            "success": True,
            "universe": universe,
            "data_source": "combinations_table",
            "table": table_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la table réelle: {str(e)}")

@router.get("/{universe}/chip/{chip_number}")
async def get_real_chip_data(
    universe: str,
    chip_number: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les données réelles d'un chip depuis 'combinations'
    Format: chip1 avec tiroirs forme + dénominations
    """
    try:
        chip_data = KatulaCombinationsService.get_chip_from_combinations(db, universe, chip_number)
        
        if "error" in chip_data:
            raise HTTPException(status_code=404, detail=chip_data["error"])
        
        return {
            "success": True,
            "chip_data": chip_data,
            "data_source": "combinations_table"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du chip réel: {str(e)}")

@router.get("/{universe}/denomination/{denomination}")
async def get_combinations_by_denomination(
    universe: str,
    denomination: str,
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les combinaisons pour une dénomination
    Exemple: /api/katula-real/mundo/denomination/table 2
    """
    try:
        combinations = KatulaCombinationsService.get_combinations_by_denomination(db, universe, denomination)
        
        return {
            "success": True,
            "universe": universe,
            "denomination": denomination,
            "combinations": combinations,
            "total": len(combinations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des combinaisons: {str(e)}")

@router.get("/{universe}/html", response_class=HTMLResponse)
async def get_real_table_html(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Génère le HTML de la vraie table de Katula
    """
    try:
        table_data = KatulaCombinationsService.get_katula_table_from_combinations(db, universe)
        
        if "error" in table_data:
            return f"<html><body><h1>Erreur</h1><p>{table_data['error']}</p></body></html>"
        
        # Générer le HTML
        html_content = _generate_katula_html(table_data)
        
        return html_content
        
    except Exception as e:
        return f"<html><body><h1>Erreur</h1><p>Erreur lors de la génération du HTML: {str(e)}</p></body></html>"

@router.get("/{universe}/summary")
async def get_table_summary(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Résumé de la table de Katula avec statistiques
    """
    try:
        table_data = KatulaCombinationsService.get_katula_table_from_combinations(db, universe)
        
        if "error" in table_data:
            raise HTTPException(status_code=500, detail=table_data["error"])
        
        # Calculer les statistiques
        total_chips = 0
        chips_with_data = 0
        total_denominations = 0
        formes_count = {}
        
        for chip_info in table_data["chips"].values():
            total_chips += 1
            has_data = False
            
            for drawer_name, drawer_info in chip_info["drawers"].items():
                if drawer_info.get("has_data", False):
                    has_data = True
                    count = len(drawer_info.get("denominations", []))
                    total_denominations += count
                    
                    if drawer_name not in formes_count:
                        formes_count[drawer_name] = 0
                    formes_count[drawer_name] += count
            
            if has_data:
                chips_with_data += 1
        
        return {
            "success": True,
            "universe": universe,
            "summary": {
                "total_chips": total_chips,
                "chips_with_data": chips_with_data,
                "chips_empty": total_chips - chips_with_data,
                "total_denominations": total_denominations,
                "formes_distribution": formes_count,
                "data_source": table_data.get("data_source", "combinations_table"),
                "last_updated": table_data.get("last_updated")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du résumé: {str(e)}")

def _generate_katula_html(table_data: dict) -> str:
    """Génère le HTML pour la table de Katula"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Table de Katula Réelle - {table_data['universe'].upper()}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            
            .katula-container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                border-radius: 8px;
            }}
            
            .info-badge {{
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                margin: 5px;
            }}
            
            .katula-grid {{
                display: grid;
                grid-template-columns: 80px repeat(6, 1fr);
                gap: 5px;
                background: #ecf0f1;
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #bdc3c7;
            }}
            
            .grid-header, .ligne-label {{
                background: #2c3e50;
                color: white;
                padding: 10px;
                text-align: center;
                font-weight: bold;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .ligne-label {{
                background: #34495e;
            }}
            
            .chip-cell {{
                background: white;
                border-radius: 8px;
                padding: 8px;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }}
            
            .chip-cell:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            
            .chip-header {{
                font-weight: bold;
                margin-bottom: 6px;
                color: #2c3e50;
                text-align: center;
                font-size: 0.9em;
                padding-bottom: 4px;
                border-bottom: 1px solid #eee;
            }}
            
            .chip-content {{
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 3px;
            }}
            
            .drawer {{
                background: #f8f9fa;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 0.75em;
                border-left: 3px solid #ddd;
                transition: all 0.2s;
            }}
            
            .drawer.has-data {{
                background: #e8f5e8;
            }}
            
            .drawer:hover {{
                background: #e9ecef;
                transform: translateX(2px);
            }}
            
            .drawer-content {{
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            
            .drawer-icon {{
                font-size: 1.1em;
                min-width: 16px;
            }}
            
            .drawer-text {{
                flex: 1;
                font-weight: 500;
                color: #2c3e50;
                word-break: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="katula-container">
            <div class="header">
                <h1>Table de Katula Réelle - {table_data['universe'].upper()}</h1>
                <p>Matrice {table_data['dimensions']['rows']}x{table_data['dimensions']['columns']} - {table_data['dimensions']['total_chips']} chips</p>
                <div>
                    <span class="info-badge">Source: {table_data.get('data_source', 'combinations')}</span>
                    <span class="info-badge">Entrées: {table_data.get('total_data_entries', 0)}</span>
                    <span class="info-badge">Statut: {table_data.get('data_status', 'loaded')}</span>
                </div>
            </div>
            
            <div class="katula-grid">
    """
    
    # En-têtes des colonnes
    html += "<div class='grid-header'></div>"  # Coin vide
    for col in range(1, 7):
        html += f"<div class='grid-header'>C{col}</div>"
    
    # Lignes de la matrice
    for row_idx, row in enumerate(table_data["matrix"]):
        # En-tête de ligne
        html += f"<div class='ligne-label'>L{row_idx + 1}</div>"
        
        # Cellules de la ligne
        for cell in row:
            html += f"""
            <div class='chip-cell'>
                <div class='chip-header'>{cell['chip_name']}</div>
                <div class='chip-content'>
            """
            
            # Tiroirs du chip
            for drawer_name, drawer_info in cell["drawers"].items():
                css_class = "drawer"
                if drawer_info.get("has_data", False):
                    css_class += " has-data"
                
                html += f"""
                <div class='{css_class}' style='border-left-color: {drawer_info["color"]}'>
                    <div class='drawer-content'>
                        <span class='drawer-icon'>{drawer_info["icon"]}</span>
                        <span class='drawer-text'>{drawer_info.get("display_text", "")}</span>
                    </div>
                </div>
                """
            
            html += """
                </div>
            </div>
            """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html