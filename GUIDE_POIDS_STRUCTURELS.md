# 🎯 Guide: Intégration des Poids Structurels Katula

## ✅ Ce qui a été implémenté

### 1. Service de Poids Structurels
**Fichier**: `backend/app/services/structural_weight_service.py`

Le service calcule automatiquement:
- ✅ **Cardinalité**: Nombre de combinaisons pour chaque élément
- ✅ **Probabilité**: Chance d'apparition basée sur la structure
- ✅ **Gap Attendu**: Nombre moyen de tirages entre apparitions
- ✅ **Score Normalisé**: Comparaison gap actuel vs gap attendu

### 2. API REST Complète
**Fichier**: `backend/app/routes/structural_weights.py`

Endpoints disponibles:
```
GET /api/structural-weights/{universe}/{attribute_type}/{attribute_value}
GET /api/structural-weights/{universe}/{attribute_type}
GET /api/structural-weights/{universe}/statistics
GET /api/structural-weights/gap-score
GET /api/structural-weights/predict-appearance
GET /api/structural-weights/cardinality
```

### 3. Documentation Technique
**Fichier**: `docs/STRUCTURAL_WEIGHTS_SPEC.md`

Spécification complète avec:
- Formules mathématiques
- Structure de données
- Cas d'usage
- Exemples concrets

### 4. Script de Test
**Fichier**: `backend/test_structural_weights.py`

Tests automatisés pour valider:
- Calculs de cardinalité
- Scores de gap
- Prédictions
- Validation mathématique

## 🔢 Cardinalités par Univers

### Mundo: 544 combinaisons
```
Total: 544 paires 2-à-2
Chips: 48 (répartition inégale)
Lignes: 8 (≈72 combos/ligne)
Colonnes: 8
Formes: 4
```

### Autres Univers
```
Fruity:   435 combinaisons
Trigga:   300 combinaisons
Roaster:  171 combinaisons
Sunshine: 153 combinaisons
```

## 📊 Exemples Concrets

### Exemple 1: Chip 5 dans Mundo

**Données structurelles**:
```json
{
  "cardinality": 15,
  "total_universe": 544,
  "probability": 0.027574,
  "expected_gap": 36.27
}
```

**Interprétation**:
- Le chip 5 contient 15 combinaisons sur 544
- Probabilité d'apparition: 2.76% par tirage
- En moyenne, apparaît tous les 36.27 tirages

**Analyse de gap**:
```
Gap actuel = 40 tirages
Gap attendu = 36.27 tirages
Score = 40 / 36.27 = 1.10

→ Le chip est légèrement "froid" (10% au-dessus de l'attendu)
```

### Exemple 2: Ligne 1 dans Mundo

**Données structurelles**:
```json
{
  "cardinality": 72,
  "total_universe": 544,
  "probability": 0.132353,
  "expected_gap": 7.55
}
```

**Interprétation**:
- Ligne 1 contient 72 combinaisons
- Probabilité: 13.24% par tirage
- Apparaît tous les 7.55 tirages en moyenne

**Analyse de gap**:
```
Gap actuel = 10 tirages
Gap attendu = 7.55 tirages
Score = 10 / 7.55 = 1.32

→ La ligne est "froide" (32% au-dessus de l'attendu)
```

## 🚀 Utilisation de l'API

### 1. Récupérer le Poids d'un Élément

```bash
curl "http://localhost:8000/api/structural-weights/mundo/chip/chip_5"
```

**Réponse**:
```json
{
  "universe": "mundo",
  "attribute_type": "chip",
  "attribute_value": "chip_5",
  "cardinality": 15,
  "total_universe": 544,
  "probability": 0.027574,
  "expected_gap": 36.27,
  "weight": 0.027574
}
```

### 2. Calculer un Score de Gap

```bash
curl "http://localhost:8000/api/structural-weights/gap-score?current_gap=40&universe=mundo&attribute_type=chip&attribute_value=chip_5"
```

**Réponse**:
```json
{
  "current_gap": 40,
  "expected_gap": 36.27,
  "gap_score": 1.10,
  "interpretation": "froid"
}
```

### 3. Prédire une Apparition

```bash
curl "http://localhost:8000/api/structural-weights/predict-appearance?current_gap=40&n_draws=10&universe=mundo&attribute_type=chip&attribute_value=chip_5"
```

**Réponse**:
```json
{
  "current_gap": 40,
  "n_draws": 10,
  "probability": 0.243,
  "percentage": "24.3%",
  "expected_gap": 36.27
}
```

### 4. Obtenir Toutes les Lignes

```bash
curl "http://localhost:8000/api/structural-weights/mundo/ligne"
```

**Réponse**:
```json
{
  "ligne1": {
    "cardinality": 72,
    "probability": 0.132353,
    "expected_gap": 7.55
  },
  "ligne2": {...},
  ...
}
```

## 🧪 Tester le Système

```bash
cd backend
python test_structural_weights.py
```

**Résultat attendu**:
```
🧪 TEST: Système de Poids Structurels Katula
================================================================================

📊 Test 1: Poids Structurel d'un Chip
--------------------------------------------------------------------------------
✅ Chip 5 (Mundo):
   Cardinalité: 15 combinaisons
   Total Mundo: 544 combinaisons
   Probabilité: 0.027574 (2.76%)
   Gap Attendu: 36.27 tirages
   Poids: 0.027574

📊 Test 2: Poids de Toutes les Lignes (Mundo)
--------------------------------------------------------------------------------
✅ 8 lignes trouvées:
   ligne1: 72 combos, P=0.1324, Gap=7.55
   ligne2: 68 combos, P=0.1250, Gap=8.00
   ligne3: 70 combos, P=0.1287, Gap=7.77
   ... et 5 autres lignes

...
```

## 💡 Intégration dans Vos Analyses

### Dans le Code Frontend

```javascript
// Récupérer le poids structurel
async function getStructuralWeight(universe, attributeType, attributeValue) {
    const response = await fetch(
        `${API_BASE}/structural-weights/${universe}/${attributeType}/${attributeValue}`
    );
    return await response.json();
}

// Calculer un score normalisé
async function calculateNormalizedScore(gap, universe, type, value) {
    const weight = await getStructuralWeight(universe, type, value);
    return gap / weight.expected_gap;
}

// Exemple d'utilisation
const chip5Weight = await getStructuralWeight('mundo', 'chip', 'chip_5');
console.log(`Gap attendu pour chip 5: ${chip5Weight.expected_gap} tirages`);

const score = await calculateNormalizedScore(40, 'mundo', 'chip', 'chip_5');
console.log(`Score normalisé: ${score.toFixed(2)}`);
```

### Dans les Services Backend

```python
from app.services.structural_weight_service import StructuralWeightService

# Dans votre service d'analyse
def analyze_element_with_weights(self, element, universe):
    # Récupérer le poids structurel
    weight = StructuralWeightService.get_structural_weight(
        self.db, universe, 'chip', element
    )
    
    # Calculer le score normalisé
    current_gap = self.get_current_gap(element)
    score = current_gap / weight['expected_gap']
    
    # Interpréter
    if score < 1.0:
        status = "chaud"
    elif score > 1.5:
        status = "très froid"
    else:
        status = "normal"
    
    return {
        'element': element,
        'gap': current_gap,
        'expected_gap': weight['expected_gap'],
        'score': score,
        'status': status
    }
```

## 📈 Avantages

### 1. Statistiques Plus Justes
- ✅ Comparaisons équitables entre éléments de tailles différentes
- ✅ Scores normalisés et comparables
- ✅ Prise en compte de la structure réelle

### 2. Prédictions Plus Précises
- ✅ Probabilités basées sur la cardinalité réelle
- ✅ Gaps attendus calculés mathématiquement
- ✅ Détection fine des anomalies

### 3. Analyses Plus Élaborées
- ✅ Pondération correcte des moyennes
- ✅ Identification des sur/sous-représentations
- ✅ Calculs statistiques rigoureux

## 🔄 Prochaines Étapes

### 1. Intégration dans l'Interface
- Afficher les gaps attendus dans les tableaux
- Colorer les cellules selon le score normalisé
- Ajouter des tooltips avec les détails structurels

### 2. Analyses Avancées
- Créer des heatmaps de scores normalisés
- Générer des rapports de prédiction
- Comparer les performances entre univers

### 3. Optimisation
- Mettre en cache les poids structurels
- Pré-calculer les statistiques fréquentes
- Optimiser les requêtes de cardinalité

## 📞 Support

**Documentation**:
- Spécification: `docs/STRUCTURAL_WEIGHTS_SPEC.md`
- Service: `backend/app/services/structural_weight_service.py`
- Routes: `backend/app/routes/structural_weights.py`
- Tests: `backend/test_structural_weights.py`

**Exemples d'utilisation**:
- Voir le script de test pour des exemples concrets
- Consulter la spécification pour les formules mathématiques
- Tester l'API avec curl ou Postman

---

**🎉 Le système de poids structurels est maintenant opérationnel!**

Vous pouvez maintenant calculer des statistiques plus justes et élaborées, basées sur la taille naturelle de chaque élément dans l'univers.

**Version**: 1.0  
**Date**: Janvier 2025  
**Statut**: ✅ Implémenté et testé
