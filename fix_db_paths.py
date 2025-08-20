#!/usr/bin/env python3
import os

# Lire le fichier analytics.py
with open("backend/app/routes/analytics.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remplacer tous les chemins relatifs par des chemins absolus
content = content.replace(
    'db_path = "backend/data/katula.db"',
    'db_path = os.path.join(os.getcwd(), "backend", "data", "katula.db")'
)

# Écrire le fichier modifié
with open("backend/app/routes/analytics.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Chemins de base de données corrigés!")