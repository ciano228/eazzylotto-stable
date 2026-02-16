# Service de Journal Statistique

## 📋 Vue d'ensemble

Le `JournalService` est le service de logique métier qui génère des journaux statistiques basés sur les **vraies données de la base de données**. Il remplace les anciennes méthodes de simulation par des requêtes réelles à la BD.

## 🎯 Problème résolu

**Avant**: Les entrées de journal étaient générées avec des données simulées/fictives, ce qui causait des incohérences comme:
- Combinaison 34-38 affichée dans l'univers "mundo" alors qu'elle appartient à "roaster"
- Formes, granques, petiques incorrects
- Aucune validation avec la base de données

**Après**: Toutes les données proviennent directement de la base de données via le `CombinationService`.

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend/API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JournalService  │  ← Service de logique métier
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│CombinationService│  ← Accès aux données BD
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Base de données│
│   (SQLite/PG)   │
└─────────────────┘
```

## 📦 Fonctionnalités

### 1. Génération d'entrée unique
```python
from app.services.journal_service import JournalService

# Générer l'entrée pour une combinaison
entry = JournalService.generate_journal_entry(db, 34, 38)

# Résultat:
{
    "combination": [34, 38],
    "num1": 34,
    "num2": 38,
    "univers": "roaster",      # ✓ Données réelles de la BD
    "forme": "carre",
    "granque": "Q6",
    "petique": "q4",
    "tome": "tome3",
    "denomination": "...",
    "engine": "...",
    "beastie": "...",
    ...
}
```

### 2. Journal complet d'un tirage
```python
# Générer le journal pour tous les numéros d'un tirage
numbers = [34, 38, 12, 45]
journal = JournalService.generate_full_journal(db, numbers)

# Résultat:
{
    "input_numbers": [34, 38, 12, 45],
    "total_combinations": 6,
    "valid_entries": 6,
    "errors": 0,
    "journal_entries": [...],
    "by_universe": {
        "mundo": [...],
        "roaster": [...],
        ...
    },
    "character_analysis": {
        "tome": {...},
        "forme": {...},
        "granque": {...},
        ...
    }
}
```

### 3. Validation d'univers
```python
# Valider que toutes les combinaisons appartiennent à un univers
validation = JournalService.validate_draw_universe(db, numbers, "mundo")

# Résultat:
{
    "is_valid": False,
    "expected_universe": "mundo",
    "total_combinations": 6,
    "valid_combinations": 4,
    "invalid_combinations": [
        {
            "combination": [34, 38],
            "expected_universe": "mundo",
            "actual_universe": "roaster"
        }
    ],
    "universe_distribution": {...}
}
```

## 🌐 API Endpoints

### POST `/api/journal/generate`
Génère le journal statistique pour un tirage.

**Request:**
```json
{
    "numbers": [34, 38, 12, 45],
    "universe": "mundo"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "input_numbers": [34, 38, 12, 45],
        "total_combinations": 6,
        "journal_entries": [...],
        ...
    }
}
```

### POST `/api/journal/validate-universe`
Valide que toutes les combinaisons appartiennent à l'univers spécifié.

**Request:**
```json
{
    "numbers": [34, 38, 12, 45],
    "universe": "mundo"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "is_valid": false,
        "invalid_combinations": [...],
        ...
    }
}
```

### GET `/api/journal/combination/{num1}/{num2}`
Récupère l'entrée de journal pour une combinaison spécifique.

**Example:** `GET /api/journal/combination/34/38`

**Response:**
```json
{
    "success": true,
    "data": {
        "combination": [34, 38],
        "univers": "roaster",
        "forme": "carre",
        ...
    }
}
```

## 🧪 Tests

Exécuter les tests:
```bash
cd backend
python test_journal_service.py
```

Les tests vérifient:
1. ✓ Récupération correcte d'une combinaison unique
2. ✓ Génération d'un journal complet
3. ✓ Validation d'univers

## 📊 Analyse par caractère

Le service analyse automatiquement les entrées par:
- **Tome**: Distribution des combinaisons par tome
- **Forme**: Distribution par forme géométrique
- **Granque**: Distribution par granque
- **Petique**: Distribution par quadrant
- **Univers**: Distribution par univers
- **Denomination**: Distribution par dénomination

Exemple:
```json
{
    "character_analysis": {
        "tome": {
            "tome1": {
                "count": 2,
                "combinations": [[1, 2], [3, 4]]
            },
            "tome3": {
                "count": 1,
                "combinations": [[34, 38]]
            }
        },
        "forme": {
            "carre": {
                "count": 3,
                "combinations": [...]
            }
        }
    }
}
```

## 🔧 Intégration dans votre code

### Dans un endpoint FastAPI:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.journal_service import JournalService

@router.post("/my-endpoint")
def my_endpoint(numbers: List[int], db: Session = Depends(get_db)):
    journal = JournalService.generate_full_journal(db, numbers)
    return journal
```

### Dans un script Python:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.journal_service import JournalService

engine = create_engine("sqlite:///./data/katula.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    journal = JournalService.generate_full_journal(db, [34, 38, 12])
    print(journal)
finally:
    db.close()
```

## ⚠️ Notes importantes

1. **Toujours utiliser une session DB**: Le service nécessite une session SQLAlchemy active
2. **Gestion des erreurs**: Les combinaisons non trouvées retournent un objet avec `"error"` au lieu de lever une exception
3. **Performance**: Pour de gros tirages, considérer la mise en cache des résultats
4. **Validation**: Toujours valider les numéros d'entrée avant d'appeler le service

## 🚀 Prochaines étapes

- [ ] Ajouter la mise en cache des résultats
- [ ] Implémenter l'analyse temporelle
- [ ] Ajouter des statistiques avancées
- [ ] Créer des visualisations graphiques
- [ ] Intégrer avec le système de prédiction ML

## 📞 Support

Pour toute question ou problème, consulter:
- Documentation principale: `README.md`
- Code source: `backend/app/services/journal_service.py`
- Tests: `backend/test_journal_service.py`
