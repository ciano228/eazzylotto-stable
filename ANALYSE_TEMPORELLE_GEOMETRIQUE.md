# 🔍 Analyse Temporelle Géométrique Katula

## 📋 Vue d'ensemble

L'analyse temporelle géométrique est une approche avancée pour identifier et tracker des zones répétitives en plaçant les résultats passés sur la table de Katula selon leur position géométrique dans le temps.

## 🎯 Principe de Base

### Étape 1: Décomposition du Tirage
Pour chaque tirage (ex: 80-72-89-50-26), on génère **toutes les combinaisons 2 à 2** :
- 80-72, 80-89, 80-50, 80-26
- 72-89, 72-50, 72-26  
- 89-50, 89-26
- 50-26

**Total: 10 combinaisons** pour un tirage de 5 numéros.

### Étape 2: Mapping Géométrique
Chaque combinaison est reliée à sa **dénomination** dans la base de données Katula, puis à sa **position géométrique** sur la table 8x6 :
- Ligne (1-8)
- Colonne (1-6) 
- Coordonnées (ex: "34" = ligne 3, colonne 4)
- Quadrant (Q1, Q2, Q3, Q4)
- Zone géométrique (top_left, middle_center, etc.)

### Étape 3: Visualisation Temporelle
Les positions sont marquées sur plusieurs tables Katula représentant différentes périodes :
- **Points/Croix** : Occurrences simples
- **Couleurs** : Intensité selon fréquence
- **Compteurs** : Nombre d'apparitions

## 🛠️ Architecture Technique

### Services Backend
```
temporal_geometric_service.py
├── analyze_temporal_patterns()     # Analyse principale
├── _map_combinations_to_geometry() # Mapping BD → Géométrie  
├── _analyze_geometric_recurrence() # Détection récurrences
├── _detect_hot_zones()            # Zones chaudes
└── _generate_predictions()        # Prédictions
```

### API Endpoints
```
POST /api/analytics/temporal-analysis/{universe}
GET  /api/analytics/temporal-data/{universe}
POST /api/analytics/geometric-mapping/{universe}  
GET  /api/analytics/temporal-periods/{universe}
```

### Interface Web
```
katula-temporal-analysis.html
├── Configuration multi-tables
├── Options de marquage avancées
├── Détection de patterns automatique
└── Visualisation comparative
```

## 📊 Types d'Analyses

### 1. Récurrences Géométriques
- **Positions répétitives** : Même coordonnée sur plusieurs périodes
- **Consistance temporelle** : Régularité des intervalles
- **Confiance** : Basée sur fréquence + consistance

### 2. Cycles Temporels
- **Cycles hebdomadaires** : Patterns par jour de la semaine
- **Cycles mensuels** : Patterns par mois
- **Cycles personnalisés** : Périodes définies par l'utilisateur

### 3. Zones Chaudes
- **Quadrants actifs** : Q1, Q2, Q3, Q4 avec forte activité
- **Zones géométriques** : 9 zones (top_left → bottom_right)
- **Seuils d'activité** : >15% pour zones, >30% pour quadrants

### 4. Prédictions
- **Récurrences fortes** : Positions avec >70% confiance
- **Cycles détectés** : Basé sur patterns temporels
- **Zones chaudes** : Surveillance des zones actives

## 🎮 Utilisation Pratique

### Démarrage Rapide
```bash
# 1. Démarrer le serveur
python simple_server.py

# 2. Ouvrir l'interface
http://localhost:8881/frontend/katula-temporal-analysis.html

# 3. Tester avec l'exemple
Cliquer "Test Mapping Géométrique" → [80,72,89,50,26]
```

### Configuration des Tables
1. **Nombre de tables** : 2-12 tables comparatives
2. **Périodes** : Historique vs Prédiction
3. **Dates** : Plages personnalisées
4. **Types** : Mensuel, trimestriel, annuel

### Options de Marquage
- **Par Chip** : Marquage individuel
- **Par Dénomination** : Groupement par nom
- **Par Tome/Granque** : Groupement structurel
- **Par Zone** : Groupement géométrique

## 📈 Exemple Concret

### Tirage: [80, 72, 89, 50, 26]

**Combinaisons générées:**
```
1. 80-72 → Position 23 (Ligne 2, Col 3) → Q1_top_left
2. 80-89 → Position 45 (Ligne 4, Col 5) → Q2_top_right  
3. 80-50 → Position 67 (Ligne 6, Col 7) → Q3_bottom_left
4. 80-26 → Position 12 (Ligne 1, Col 2) → Q1_top_left
5. 72-89 → Position 34 (Ligne 3, Col 4) → Q2_top_right
... (5 autres combinaisons)
```

**Analyse résultante:**
- **Quadrant Q1** : 2 occurrences (20%)
- **Quadrant Q2** : 2 occurrences (20%) 
- **Zone top_left** : Activité élevée
- **Prédiction** : Surveiller Q1 et Q2 pour prochains tirages

## 🔧 Configuration Avancée

### Base de Données
```python
# Configuration PostgreSQL
db_config = {
    'host': 'localhost',
    'database': 'katooling_main_system', 
    'user': 'postgres',
    'password': 'your_password'
}
```

### Paramètres d'Analyse
```python
period_config = {
    'period_type': 'monthly',      # weekly, monthly, quarterly
    'analyze_by_period': True,     # Groupement par période
    'confidence_threshold': 70,    # Seuil de confiance (%)
    'min_occurrences': 2          # Occurrences minimales
}
```

## 🎯 Avantages de l'Approche

### 1. **Précision Géométrique**
- Mapping exact des combinaisons sur la table
- Prise en compte de la structure spatiale
- Détection de patterns géométriques invisibles

### 2. **Analyse Temporelle**
- Comparaison multi-périodes
- Détection de cycles récurrents  
- Prédictions basées sur l'historique

### 3. **Visualisation Intuitive**
- Tables Katula côte à côte
- Marquage coloré par fréquence
- Navigation interactive

### 4. **Flexibilité**
- Multiple types de marquage
- Périodes configurables
- Filtres avancés

## 🚀 Développements Futurs

### Phase 1 (Actuelle)
- ✅ Mapping géométrique de base
- ✅ Interface multi-tables
- ✅ Détection patterns simples

### Phase 2 (Prochaine)
- 🔄 Intégration données réelles BD
- 🔄 Machine Learning pour prédictions
- 🔄 Export/Import configurations

### Phase 3 (Future)
- 📋 Analyse cross-univers
- 📋 Patterns complexes multi-niveaux
- 📋 API temps réel

## 📞 Support

Pour questions techniques ou améliorations :
- Consulter les logs du serveur
- Tester avec `test_geometric_approach.py`
- Vérifier la connectivité BD PostgreSQL

---

**Version**: 1.0.0  
**Dernière mise à jour**: $(date)  
**Statut**: Implémentation complète