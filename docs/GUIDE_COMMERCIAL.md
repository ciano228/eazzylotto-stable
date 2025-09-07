# Guide de Démarrage EazzyCalculator

## Installation

1. **Prérequis**
   - Python 3.8 ou supérieur
   - PostgreSQL 12 ou supérieur
   - Navigateur web moderne
   - 2 Go RAM minimum

2. **Configuration Environnement**
   ```bash
   # Créer l'environnement virtuel
   python -m venv venv
   
   # Activer l'environnement
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Installer les dépendances
   pip install -r requirements.txt
   ```

3. **Configuration Base de Données**
   ```bash
   # Copier le fichier de configuration
   cp .env.example .env
   
   # Éditer les paramètres dans .env
   # Notamment DATABASE_URL et SECRET_KEY
   
   # Initialiser la base de données
   python backend/init_db.py
   ```

4. **Démarrage des Serveurs**
   ```bash
   # Démarrer en mode production
   python deploy_production.py
   ```

## Accès à l'Application

- **Interface Utilisateur**: http://localhost:8080
- **API Backend**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## Fonctionnalités Principales

1. **Table de Katula**
   - Visualisation géométrique des combinaisons
   - Analyse temporelle des patterns
   - Prédictions basées sur l'historique

2. **Analyses Avancées**
   - Analyse multidimensionnelle
   - Détection de patterns
   - Prédictions par apprentissage automatique

3. **Interface Utilisateur**
   - Dashboard personnalisable
   - Visualisations interactives
   - Export des données et rapports

## Support et Maintenance

- **Email Support**: support@eazzycalculator.com
- **Documentation**: http://localhost:8080/docs
- **Mises à jour**: Vérification automatique des mises à jour

## Sécurité

- Authentification JWT
- Chiffrement des données sensibles
- Rate limiting
- Protection contre les injections SQL

## Sauvegarde et Récupération

1. **Sauvegarde Automatique**
   ```bash
   # Configuration dans .env
   BACKUP_PATH=/path/to/backups
   BACKUP_RETENTION_DAYS=30
   ```

2. **Restauration**
   ```bash
   python scripts/restore_backup.py --date YYYY-MM-DD
   ```

## Monitoring

- Logs d'application dans /var/log/eazzycalculator
- Métriques de performance
- Alertes automatiques
- Dashboard d'administration

## Licence et Usage Commercial

Ce logiciel est protégé par copyright. Usage commercial autorisé selon les termes de la licence.
