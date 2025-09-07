"""
Route de diagnostic pour tester l'importation des modules
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_route():
    return {"status": "ok", "message": "Test route is working"}
