# Solution BD pour Table Katula

## Approche pour peupler la table avec vraies données BD

### 1. Structure BD créée
```sql
CREATE TABLE combinations (
    univers TEXT,     -- 'mundo', 'fruity', etc.
    forme TEXT,       -- 'carre', 'triangle', 'cercle', 'rectangle'  
    chip INTEGER,     -- 1 à 48
    denomination TEXT, -- 'road 1', 'tree 5', etc.
    object_name TEXT,
    num1 INTEGER,
    num2 INTEGER,
    alpha_ranking TEXT
);
```

### 2. Endpoints BD modifiés
- `/katula/chip/{universe}/{chip_number}` : Requête SQLite réelle
- `/denomination/{universe}/{denomination}` : Détails depuis BD

### 3. Logique de peuplement
```python
# Pour chaque chip (1-48) et chaque forme (carre, triangle, cercle, rectangle)
SELECT denomination, object_name 
FROM combinations 
WHERE univers = 'mundo' AND forme = 'carre' AND chip = 1
```

### 4. Données d'exemple créées
- **Chip 1** : road 1 (carré), tree 5 (triangle), house 3 (cercle)
- **Chip 2** : car 7 (carré), star 2 (rectangle)  
- **Chip 3** : moon 4 (triangle), sun 8 (cercle), flower 1 (rectangle)
- etc.

### 5. Fallback intelligent
- Si BD non disponible → tiroirs vides
- Si pas de données pour une forme → tiroir vide
- Préserve la structure 4 formes pour Mundo

## Résultat attendu
- **Mundo** : 4 formes avec vraies dénominations BD
- **Table peuplée** au lieu de table vide
- **Données cohérentes** basées sur univers/forme/chip

## Pour tester
1. Redémarrer backend : `python start_backend.py`
2. Ouvrir : http://localhost:8000/katula-dynamic.html
3. Sélectionner "Mundo" → "Charger Univers"
4. Voir les vraies dénominations dans les tiroirs