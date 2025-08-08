#!/usr/bin/env python3
"""
Script de diagnostic des imports et routes API
"""

import sys
import traceback

def test_imports():
    """Teste tous les imports nécessaires"""
    print("=== TEST DES IMPORTS ===")
    
    imports_to_test = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("CORS", "from fastapi.middleware.cors import CORSMiddleware"),
        ("StaticFiles", "from fastapi.staticfiles import StaticFiles"),
        ("Database", "from app.database.connection import engine, Base"),
        ("Lottery Router", "from app.routes.lottery import router as lottery_router"),
        ("Analysis Router", "from app.routes.analysis import router as analysis_router"),
        ("Session Router", "from app.routes.session import router as session_router"),
        ("Analytics Router", "from app.routes.analytics import router as analytics_router"),
        ("Katooling Router", "from app.routes.katooling_workflow import router as katooling_workflow_router"),
        ("Dotenv", "from dotenv import load_dotenv")
    ]
    
    success_count = 0
    for name, import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"[OK] {name}")
            success_count += 1
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            traceback.print_exc()
    
    print(f"\nImports réussis: {success_count}/{len(imports_to_test)}")
    return success_count == len(imports_to_test)

def test_simple_fastapi():
    """Teste une application FastAPI simple"""
    print("\n=== TEST FASTAPI SIMPLE ===")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Test API")
        
        @app.get("/")
        def root():
            return {"message": "Test OK"}
        
        @app.get("/api/health")
        def health():
            return {"status": "healthy"}
        
        print("[OK] Application FastAPI simple créée")
        print("[OK] Routes de base ajoutées")
        return True
        
    except Exception as e:
        print(f"[ERROR] FastAPI simple: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("\n=== TEST BASE DE DONNÉES ===")
    
    try:
        from app.database.connection import engine, Base
        
        # Tester la connexion
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("[OK] Connexion base de données")
        
        print("[OK] Import database OK")
        return True
        
    except Exception as e:
        print(f"[ERROR] Base de données: {e}")
        return False

def main():
    print("DIAGNOSTIC DES IMPORTS ET ROUTES API")
    print("=" * 50)
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    # Test 2: FastAPI simple
    fastapi_ok = test_simple_fastapi()
    
    # Test 3: Base de données
    db_ok = test_database_connection()
    
    print("\n=== RÉSUMÉ ===")
    print(f"Imports: {'OK' if imports_ok else 'ERREUR'}")
    print(f"FastAPI: {'OK' if fastapi_ok else 'ERREUR'}")
    print(f"Base de données: {'OK' if db_ok else 'ERREUR'}")
    
    if not imports_ok:
        print("\n[SOLUTION] Problème d'imports détecté")
        print("Les routes ne peuvent pas être chargées à cause d'erreurs d'importation")
    
    return imports_ok and fastapi_ok

if __name__ == "__main__":
    main()
