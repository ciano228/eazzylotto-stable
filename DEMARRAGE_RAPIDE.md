# 🚀 Guide de Démarrage Rapide - EazzyCalculator

## ✅ Prérequis

- Python 3.9+
- PostgreSQL 12+ (avec base `katooling_main_system`)
- pip

## 📦 Installation

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Le fichier `.env` est déjà configuré avec les valeurs par défaut:

```env
DATABASE_URL=postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system
DB_NAME=katooling_main_system
DB_USER=postgres
DB_PASSWORD=Katulaa_33
DB_HOST=localhost
DB_PORT=5432
```

⚠️ **Important**: Modifiez ces valeurs si votre configuration PostgreSQL est différente.

## 🎯 Démarrage

### Option 1: Script de démarrage (Recommandé)

```bash
# Depuis la racine du projet
python start_backend.py
```

### Option 2: Serveur intégré

```bash
# Depuis la racine du projet
python integrated_server.py
```

### Option 3: Démarrage manuel

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

## 🌐 Accès aux interfaces

Une fois le serveur démarré:

- **API Documentation**: http://localhost:8000/api/docs
- **API Alternative**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health
- **Frontend**: http://localhost:8000/

## 🔧 Fonctionnalités disponibles

### API Endpoints principaux

#### Authentification
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `GET /api/auth/me` - Informations utilisateur

#### Katula
- `GET /api/katula/table/{universe}` - Table Katula
- `GET /api/katula/analysis/{universe}` - Analyse patterns
- `GET /api/katula/prediction/{universe}` - Prédictions

#### Journal Statistique
- `POST /journal/generate` - Générer journal
- `POST /journal/validate-universe` - Valider univers
- `GET /journal/combination/{num1}/{num2}` - Combinaison spécifique

#### Analytics
- `GET /analytics/chip-drawers-structure/{universe}` - Structure drawers
- `GET /analytics/temporal-periods/{universe}` - Périodes temporelles

## 🧪 Tests

### Test de connexion API

```bash
curl http://localhost:8000/api/health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "version": "EazzyCalculator v2.0.0",
  "database": "connected",
  "environment": "development"
}
```

### Test du journal statistique

```bash
curl -X POST http://localhost:8000/journal/generate \
  -H "Content-Type: application/json" \
  -d '{"numbers": [1, 2, 3, 4, 5]}'
```

## 📊 Structure du projet

```
eazzycalculator/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration et auth
│   │   ├── database/      # Connexion DB
│   │   ├── models/        # Modèles SQLAlchemy
│   │   ├── routes/        # Endpoints API
│   │   ├── schemas/       # Modèles Pydantic
│   │   ├── services/      # Logique métier
│   │   └── utils/         # Utilitaires
│   ├── main.py           # Point d'entrée
│   ├── requirements.txt  # Dépendances
│   └── .env             # Configuration
├── frontend/            # Interface utilisateur
├── integrated_server.py # Serveur intégré
└── start_backend.py    # Script de démarrage
```

## 🐛 Dépannage

### Erreur de connexion à la base de données

1. Vérifier que PostgreSQL est démarré
2. Vérifier les credentials dans `.env`
3. Tester la connexion:

```bash
psql -U postgres -d katooling_main_system -h localhost
```

### Port déjà utilisé

Si le port 8000 est occupé, modifier dans `.env`:

```env
PORT=8001
```

### Modules manquants

```bash
cd backend
pip install -r requirements.txt --upgrade
```

## 📚 Documentation complète

- [README Principal](README.md)
- [État du Système](ETAT_REEL_SYSTEME.md)
- [Résumé Final](RESUME_FINAL.md)
- [Service Journal](docs/JOURNAL_SERVICE.md)

## 🆘 Support

Pour toute question ou problème:
1. Vérifier les logs du serveur
2. Consulter la documentation API: http://localhost:8000/api/docs
3. Vérifier les fichiers de documentation dans `/docs`

---

**Version**: 2.0.2  
**Dernière mise à jour**: 2024  
**Statut**: ✅ Fonctionnel
