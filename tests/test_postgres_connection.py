import sys
import os
sys.path.append('backend')

from database_postgresql import test_connection, get_postgres_connection

print("=== TEST CONNEXION POSTGRESQL ===")

# Test de connexion
success, result = test_connection()
if success:
    print(f"✅ Connexion réussie: {result}")
    
    # Test des données
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Vérifier les univers
        cursor.execute("SELECT DISTINCT univers FROM katooling_main_system LIMIT 5")
        univers = cursor.fetchall()
        print(f"✅ Univers disponibles: {[u[0] for u in univers]}")
        
        # Test Mundo
        cursor.execute("""
        SELECT DISTINCT forme, COUNT(*) as freq 
        FROM katooling_main_system 
        WHERE univers = 'mundo' AND forme IS NOT NULL 
        GROUP BY forme ORDER BY freq DESC LIMIT 5
        """)
        mundo_formes = cursor.fetchall()
        print(f"✅ Mundo formes: {mundo_formes}")
        
        conn.close()
        print("🎉 Base PostgreSQL prête!")
        
    except Exception as e:
        print(f"❌ Erreur données: {e}")
        
else:
    print(f"❌ Connexion échouée: {result}")
    print("💡 Vérifiez les paramètres PostgreSQL dans .env")