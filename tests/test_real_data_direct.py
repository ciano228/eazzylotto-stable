import sqlite3
import json
import os

# Connexion à la base de données
db_path = os.path.join('backend', 'data', 'katula.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test des données réelles
print("=== TEST DONNÉES RÉELLES ===")

# 1. Vérifier les univers disponibles
cursor.execute("SELECT DISTINCT univers FROM katooling_main_system LIMIT 10")
univers = cursor.fetchall()
print(f"Univers disponibles: {[u[0] for u in univers]}")

# 2. Tester Mundo
cursor.execute("""
SELECT DISTINCT forme, COUNT(*) as freq 
FROM katooling_main_system 
WHERE univers = 'mundo' AND forme IS NOT NULL 
GROUP BY forme ORDER BY freq DESC
""")
mundo_formes = cursor.fetchall()
print(f"\nMundo formes: {mundo_formes}")

# 3. Tester Roaster  
cursor.execute("""
SELECT DISTINCT forme, COUNT(*) as freq 
FROM katooling_main_system 
WHERE univers = 'roaster' AND forme IS NOT NULL 
GROUP BY forme ORDER BY freq DESC
""")
roaster_formes = cursor.fetchall()
print(f"Roaster formes: {roaster_formes}")

# 4. Données pour chip 1 de Mundo
cursor.execute("""
SELECT forme, denomination, COUNT(*) as freq
FROM katooling_main_system 
WHERE univers = 'mundo' AND chip = 1 AND forme IS NOT NULL
GROUP BY forme, denomination
""")
chip1_data = cursor.fetchall()
print(f"\nChip 1 Mundo: {chip1_data}")

# 5. Générer JSON pour frontend
data_export = {
    'mundo': {
        'formes': [f[0] for f in mundo_formes],
        'chip1': {}
    },
    'roaster': {
        'formes': [f[0] for f in roaster_formes], 
        'chip1': {}
    }
}

# Organiser chip 1 data
for forme, denom, freq in chip1_data:
    if forme not in data_export['mundo']['chip1']:
        data_export['mundo']['chip1'][forme] = []
    data_export['mundo']['chip1'][forme].append({'denomination': denom, 'frequency': freq})

print(f"\nDonnées exportées: {json.dumps(data_export, indent=2)}")

conn.close()