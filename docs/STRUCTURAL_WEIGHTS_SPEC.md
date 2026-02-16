# 📊 Spécification: Poids Structurels Katula

## 🎯 Objectif

Intégrer les **cardinalités structurelles** de chaque chip et attribut pour calculer des statistiques plus justes et élaborées, basées sur le poids naturel de chaque élément dans l'univers.

## 📐 Principe Fondamental

Chaque chip et chaque valeur d'attribut a une **taille naturelle** (nombre de combinaisons qu'il contient) qui détermine sa **probabilité d'apparition** dans un tirage aléatoire.

### Exemple: Univers Mundo
- **Total combinaisons**: 544 (toutes les paires 2-à-2)
- **Nombre de chips**: 48
- **Répartition inégale**: Chaque chip contient un nombre différent de combinaisons

### Exemple: Attribut Ligne (Mundo)
- **Total combinaisons**: 544
- **Nombre de lignes**: 8 (ligne1, ligne2, ..., ligne8)
- **Ligne 1**: 72 combinaisons
- **Probabilité ligne1**: 72/544 = 13.24%

## 🔢 Cardinalités par Univers

### Mundo
```
Total: 544 combinaisons
Chips: 48 (répartition inégale)
Lignes: 8 (72 combinaisons par ligne en moyenne)
Colonnes: 8
Formes: 4 (carré, triangle, cercle, rectangle)
```

### Fruity
```
Total: 435 combinaisons
Chips: 48 (répartition différente de Mundo)
```

### Trigga
```
Total: 300 combinaisons
Chips: 48
```

### Roaster
```
Total: 171 combinaisons
Chips: 48
```

### Sunshine
```
Total: 153 combinaisons
Chips: 48
```

## 📊 Formules de Calcul

### 1. Probabilité Structurelle
```
P(élément) = count(élément) / total_univers

Exemple:
P(chip_5_mundo) = 15 / 544 = 2.76%
P(ligne1_mundo) = 72 / 544 = 13.24%
```

### 2. Gap Attendu (Expected Gap)
```
expectedGap = 1 / P(élément)

Exemple:
expectedGap(chip_5_mundo) = 1 / 0.0276 = 36.27 tirages
expectedGap(ligne1_mundo) = 1 / 0.1324 = 7.55 tirages
```

### 3. Score de Gap Normalisé
```
gapScore = currentGap / expectedGap

Interprétation:
- gapScore < 1: L'élément apparaît plus souvent que prévu (chaud)
- gapScore = 1: L'élément apparaît comme prévu (normal)
- gapScore > 1: L'élément apparaît moins souvent que prévu (froid)
```

### 4. Poids Structurel (Structural Weight)
```
weight = count(élément) / total_univers

Usage:
- Pondération des statistiques
- Calcul de moyennes pondérées
- Normalisation des scores
```

## 🗄️ Structure de Données

### Table: structural_weights
```sql
CREATE TABLE structural_weights (
    id SERIAL PRIMARY KEY,
    universe VARCHAR(20) NOT NULL,
    attribute_type VARCHAR(50) NOT NULL,  -- 'chip', 'ligne', 'colonne', etc.
    attribute_value VARCHAR(100) NOT NULL, -- 'chip_5', 'ligne1', etc.
    cardinality INTEGER NOT NULL,         -- Nombre de combinaisons
    total_universe INTEGER NOT NULL,      -- Total combinaisons univers
    probability DECIMAL(10, 6) NOT NULL,  -- cardinality / total_universe
    expected_gap DECIMAL(10, 2) NOT NULL, -- 1 / probability
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(universe, attribute_type, attribute_value)
);
```

### Exemple de données
```sql
INSERT INTO structural_weights VALUES
('mundo', 'chip', 'chip_5', 15, 544, 0.027574, 36.27),
('mundo', 'ligne', 'ligne1', 72, 544, 0.132353, 7.55),
('mundo', 'forme', 'carre', 136, 544, 0.250000, 4.00),
('fruity', 'chip', 'chip_5', 12, 435, 0.027586, 36.25);
```

## 🔧 Implémentation

### 1. Service: StructuralWeightService
```python
class StructuralWeightService:
    @staticmethod
    def get_cardinality(db, universe, attribute_type, attribute_value):
        """Récupère la cardinalité d'un élément"""
        
    @staticmethod
    def calculate_probability(cardinality, total_universe):
        """Calcule la probabilité structurelle"""
        
    @staticmethod
    def calculate_expected_gap(probability):
        """Calcule le gap attendu"""
        
    @staticmethod
    def get_structural_weight(db, universe, attribute_type, attribute_value):
        """Récupère le poids structurel complet"""
```

### 2. Intégration dans AdvancedStatsService
```python
def calculate_gap_score_with_weights(self, current_gap, universe, attribute_type, attribute_value):
    """Calcule le score de gap avec poids structurels"""
    weight = StructuralWeightService.get_structural_weight(
        self.db, universe, attribute_type, attribute_value
    )
    expected_gap = weight['expected_gap']
    return current_gap / expected_gap
```

### 3. API Endpoint
```python
@router.get("/api/structural-weights/{universe}/{attribute_type}")
async def get_structural_weights(universe: str, attribute_type: str):
    """Récupère les poids structurels pour un univers et type d'attribut"""
```

## 📈 Cas d'Usage

### 1. Analyse de Gap
**Avant** (sans poids):
```
Chip 5: gap = 40 tirages → Score = 40/10 = 4.0 (basé sur moyenne globale)
Ligne 1: gap = 10 tirages → Score = 10/10 = 1.0
```

**Après** (avec poids):
```
Chip 5: gap = 40 tirages → Score = 40/36.27 = 1.10 (légèrement froid)
Ligne 1: gap = 10 tirages → Score = 10/7.55 = 1.32 (froid)
```

### 2. Prédiction Pondérée
```python
# Calculer la probabilité d'apparition dans les N prochains tirages
def predict_appearance(gap, expected_gap, n_draws):
    prob_per_draw = 1 / expected_gap
    prob_in_n_draws = 1 - (1 - prob_per_draw) ** n_draws
    return prob_in_n_draws
```

### 3. Scoring Multi-Attributs
```python
# Score composite basé sur plusieurs attributs
def composite_score(chip_gap, ligne_gap, forme_gap, weights):
    chip_score = chip_gap / weights['chip']['expected_gap']
    ligne_score = ligne_gap / weights['ligne']['expected_gap']
    forme_score = forme_gap / weights['forme']['expected_gap']
    
    # Moyenne pondérée
    return (chip_score + ligne_score + forme_score) / 3
```

## 🎯 Bénéfices

### 1. Statistiques Plus Justes
- Prise en compte de la taille réelle de chaque élément
- Comparaisons équitables entre éléments de tailles différentes
- Scores normalisés et comparables

### 2. Prédictions Plus Précises
- Probabilités basées sur la structure réelle
- Gaps attendus calculés mathématiquement
- Détection plus fine des anomalies

### 3. Analyses Plus Élaborées
- Pondération correcte des moyennes
- Identification des éléments sur/sous-représentés
- Calculs de variance et écart-type corrects

## 📝 Exemple Complet

### Scénario: Analyse Chip 5 dans Mundo

**Données structurelles**:
```
Chip 5 (Mundo):
- Cardinalité: 15 combinaisons
- Total Mundo: 544 combinaisons
- Probabilité: 15/544 = 2.76%
- Expected Gap: 1/0.0276 = 36.27 tirages
```

**Historique**:
```
Dernière apparition: Tirage #50
Tirage actuel: Tirage #90
Gap actuel: 40 tirages
```

**Analyse**:
```
Gap Score = 40 / 36.27 = 1.10

Interprétation:
- Le chip 5 est légèrement "froid" (10% au-dessus de l'attendu)
- Probabilité d'apparition dans les 10 prochains tirages: 24.3%
- Recommandation: Surveillance, pas encore critique
```

## 🔄 Migration

### Étape 1: Calculer les Cardinalités
```sql
-- Pour chaque univers, compter les combinaisons par attribut
SELECT 
    univers,
    chip,
    COUNT(*) as cardinality
FROM combinations
GROUP BY univers, chip;
```

### Étape 2: Peupler la Table
```python
def populate_structural_weights(db):
    universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    for universe in universes:
        total = get_total_combinations(db, universe)
        
        # Pour chaque type d'attribut
        for attr_type in ['chip', 'ligne', 'colonne', 'forme']:
            cardinalities = calculate_cardinalities(db, universe, attr_type)
            
            for value, count in cardinalities.items():
                insert_structural_weight(db, universe, attr_type, value, count, total)
```

### Étape 3: Mettre à Jour les Services
```python
# Remplacer les calculs de gap par des calculs pondérés
old: gap_score = current_gap / average_gap
new: gap_score = current_gap / expected_gap_from_weights
```

## 📊 Validation

### Tests à Effectuer
1. Vérifier que la somme des probabilités = 1 pour chaque attribut
2. Comparer les gaps attendus avec les gaps observés sur historique
3. Valider que les scores sont cohérents entre univers
4. Tester les cas limites (éléments très rares, très fréquents)

---

**Version**: 1.0  
**Date**: Janvier 2025  
**Statut**: Spécification complète - Prêt pour implémentation
