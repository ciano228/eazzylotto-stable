# EazzyLotto

## Structure du Projet

```
eazzylotto/
├── backend/
│   ├── servers/          # Différentes versions des serveurs
│   ├── analysis/         # Scripts d'analyse
│   ├── scripts/          # Scripts utilitaires
│   ├── services/         # Services métier
│   ├── database/         # Configuration et modèles de base de données
│   └── utils/           # Utilitaires généraux
├── frontend/            # Interface utilisateur
├── docs/               # Documentation du projet
├── tests/             # Tests
└── scripts/           # Scripts de déploiement et configuration
```

## Installation

1. Cloner le repository
2. Installer les dépendances avec `pip install -r requirements.txt`
3. Configurer le fichier `.env`
4. Lancer le serveur avec `python -m uvicorn backend.servers.server_postgres_simple:app --reload`

## Documentation

Toute la documentation du projet se trouve dans le dossier `docs/`.
