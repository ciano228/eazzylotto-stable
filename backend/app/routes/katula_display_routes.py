"""
Routes pour l'Affichage de la Table de Katula
API endpoints pour l'affichage formaté avec icônes et dénominations
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.database.database_postgresql import get_db
from backend.app.services.katula_display_service import KatulaDisplayService

router = APIRouter(prefix="/api/katula-display", tags=["katula-display"])

@router.get("/health")
async def health_check():
    """Vérification de santé du service d'affichage"""
    return {
        "status": "healthy",
        "service": "katula-display",
        "version": "1.0.0"
    }

@router.get("/{universe}")
async def get_formatted_table(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère la table de Katula formatée pour l'affichage
    Avec chips nommés, icônes et dénominations selon la logique métier
    """
    try:
        table_data = KatulaDisplayService.get_formatted_katula_table(db, universe)
        
        if "error" in table_data:
            raise HTTPException(status_code=500, detail=table_data["error"])
        
        return {
            "success": True,
            "universe": universe,
            "table": table_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la table formatée: {str(e)}")

@router.get("/{universe}/chip/{chip_number}")
async def get_chip_display(
    universe: str,
    chip_number: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les données d'affichage pour un chip spécifique
    Format: chip1 avec tiroirs icône + dénomination
    """
    try:
        chip_data = KatulaDisplayService.get_chip_display_data(db, universe, chip_number)
        
        if "error" in chip_data:
            raise HTTPException(status_code=404, detail=chip_data["error"])
        
        return {
            "success": True,
            "chip_data": chip_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du chip: {str(e)}")

@router.get("/{universe}/html", response_class=HTMLResponse)
async def get_table_html(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Génère le HTML complet pour l'affichage de la table de Katula
    """
    try:
        table_data = KatulaDisplayService.get_formatted_katula_table(db, universe)
        
        if "error" in table_data:
            return f"<html><body><h1>Erreur</h1><p>{table_data['error']}</p></body></html>"
        
        html_content = KatulaDisplayService.generate_html_display(table_data)
        
        # HTML complet avec CSS
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Table de Katula - {universe.upper()}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                
                .katula-table-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                
                .table-header {{
                    text-align: center;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: linear-gradient(135deg, #2c3e50, #34495e);
                    color: white;
                    border-radius: 8px;
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
                    transition: transform 0.2s, box-shadow 0.2s;
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
                
                .chip-drawer {{
                    background: #f8f9fa;
                    border-radius: 4px;
                    padding: 4px 6px;
                    font-size: 0.75em;
                    transition: all 0.2s;
                    border-left: 3px solid #ddd;
                }}
                
                .chip-drawer.has-data {{
                    background: #e8f5e8;
                }}
                
                .chip-drawer:hover {{
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
                
                .error {{
                    background: #ffebee;
                    color: #c62828;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 20px;
                }}
                
                @media (max-width: 768px) {{
                    .katula-grid {{
                        grid-template-columns: 60px repeat(6, 1fr);
                        gap: 3px;
                        padding: 10px;
                    }}
                    
                    .chip-cell {{
                        min-height: 100px;
                        padding: 6px;
                    }}
                    
                    .chip-drawer {{
                        font-size: 0.7em;
                        padding: 3px 4px;
                    }}
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return full_html
        
    except Exception as e:
        return f"<html><body><h1>Erreur</h1><p>Erreur lors de la génération du HTML: {str(e)}</p></body></html>"

@router.get("/{universe}/matrix-simple")
async def get_simple_matrix(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère une version simplifiée de la matrice pour les tests
    """
    try:
        table_data = KatulaDisplayService.get_formatted_katula_table(db, universe)
        
        if "error" in table_data:
            raise HTTPException(status_code=500, detail=table_data["error"])
        
        # Simplifier la structure pour les tests
        simple_matrix = []
        for row in table_data["matrix"]:
            simple_row = []
            for cell in row:
                simple_cell = {
                    "chip_name": cell["chip_name"],
                    "chip_number": cell["chip_number"],
                    "position": cell["position"],
                    "drawers_summary": {}
                }
                
                for drawer_name, drawer_info in cell["drawers"].items():
                    simple_cell["drawers_summary"][drawer_name] = {
                        "icon": drawer_info["icon"],
                        "has_data": drawer_info.get("has_data", False),
                        "count": len(drawer_info.get("denominations", [])),
                        "display": drawer_info.get("formatted_display", "")
                    }
                
                simple_row.append(simple_cell)
            simple_matrix.append(simple_row)
        
        return {
            "success": True,
            "universe": universe,
            "dimensions": table_data["dimensions"],
            "drawer_order": table_data["drawer_order"],
            "matrix": simple_matrix
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de la matrice simple: {str(e)}")

@router.get("/icons/list")
async def get_icons_list():
    """Retourne la liste des icônes disponibles par forme"""
    return {
        "success": True,
        "icons": KatulaDisplayService.FORME_ICONS,
        "colors": KatulaDisplayService.FORME_COLORS,
        "drawer_orders": KatulaDisplayService.DRAWER_ORDER
    }