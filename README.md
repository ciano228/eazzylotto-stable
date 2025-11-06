# EazzyCalculator - Système d'Analyse Katula

Version professionnelle du système d'analyse et de prédiction pour les jeux de loterie avec la méthode Katula.

## 🏗️ Architecture du Projet

```
eazzycalculator/
├── backend/                 # API FastAPI
│   ├── app/                # Application principale
│   │   ├── routes/         # Endpoints API
│   │   ├── services/       # Logique métier
│   │   ├── models/         # Modèles de données
│   │   └── database/       # Configuration DB
│   ├── servers/            # Serveurs de développement
│   ├── scripts/            # Scripts utilitaires
│   └── main.py            # Point d'entrée principal
├── frontend/               # Interface utilisateur
│   ├── katula-dynamic.html # Interface Katula dynamique
│   ├── test-interface.html # Interface de test
│   └── assets/            # Ressources statiques
├── docs/                  # Documentation
└── scripts/              # Scripts de déploiement
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.9+
- FastAPI
- SQLAlchemy
- PostgreSQL (optionnel, SQLite par défaut)

### Installation

1. **Cloner le repository**
```bash
git clone <votre-repo-url>
cd eazzycalculator
```

2. **Installer les dépendances**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configuration**
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
```

4. **Démarrage du serveur intégré**
```bash
# Depuis la racine du projet
python integrated_server.py
```

Ou avec le serveur FastAPI classique :
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

## 🌐 Accès aux Interfaces

- **Interface Katula Dynamique**: http://localhost:8000/katula-dynamic.html
- **Interface de Test**: http://localhost:8000/test-interface.html
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## 📊 Fonctionnalités Principales

### Analyse Katula
- Génération de matrices Katula dynamiques
- Analyse des formes et structures
- Prédictions basées sur les patterns historiques

### API Endpoints
- `/api/katula-matrix` - Génération de matrices
- `/api/universe` - Informations sur les univers
- `/api/analysis` - Services d'analyse
- `/api/combinations` - Gestion des combinaisons

### Services Avancés
- Machine Learning pour prédictions
- Analyse temporelle des patterns
- Détection d'anomalies
- Optimisation des combinaisons

## 🔧 Configuration

### Base de Données
Le système supporte SQLite (par défaut) et PostgreSQL :

```env
# SQLite (développement)
DATABASE_URL=sqlite:///./data/katula.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/katula_db
```

### Variables d'Environnement
```env
DATABASE_URL=sqlite:///./data/katula.db
SECRET_KEY=your-secret-key
DEBUG=true
```

## 🧪 Tests

```bash
cd backend
python -m pytest tests/
```

## 📈 Développement

### Structure des Services
- **KatulaService**: Logique principale Katula
- **AnalysisService**: Services d'analyse
- **CombinationService**: Gestion des combinaisons
- **MLService**: Machine Learning

### Ajout de Nouvelles Fonctionnalités
1. Créer le service dans `backend/app/services/`
2. Ajouter les routes dans `backend/app/routes/`
3. Mettre à jour les modèles si nécessaire
4. Ajouter les tests correspondants

## 🚀 Déploiement

### Développement
```bash
python integrated_server.py
```

### Production
```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 Changelog

### Version 2.0.0
- Architecture FastAPI moderne
- Interface utilisateur améliorée
- Services ML intégrés
- Support multi-base de données

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changes (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence privée. Tous droits réservés.

## 📞 Support

Pour toute question ou support technique, contactez l'équipe de développement.

---

**Version**: 2.0.0  
**Dernière mise à jour**: $(date)  
**Statut**: En développement actif