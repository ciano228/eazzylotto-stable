# EazzyCalculator - Système d'Analyse Katula

Version professionnelle du système d'analyse et de prédiction pour les jeux de loterie avec la méthode Katula.

> 🆕 **Nouveau**: Système complet et fonctionnel - **[👋 COMMENCER ICI](COMMENCER_ICI.md)**

## 🚀 DÉMARRAGE ULTRA-RAPIDE

### Windows

**Double-cliquez sur:**
- `demarrer.bat` (Invite de commandes)
- `demarrer.ps1` (PowerShell)

**Ou en ligne de commande:**
```bash
python verifier_installation.py
python start_backend.py
```

### Linux/Mac

```bash
python3 verifier_installation.py
python3 start_backend.py
```

## 📚 Documentation

### 🚀 Démarrage
- **[⚡ Vue d'Ensemble](VUE_ENSEMBLE.md)** - En 30 secondes
- **[🚀 Guide de Démarrage Rapide](DEMARRAGE_RAPIDE.md)** ⭐ COMMENCEZ ICI
- **[📚 Index de la Documentation](INDEX_DOCUMENTATION.md)** - Navigation complète

### 🔧 Corrections et Mises à Jour
- **[📋 Synthèse des Corrections](SYNTHESE_CORRECTIONS.md)** - Vue d'ensemble
- **[📝 Liste des Changements](LISTE_CHANGEMENTS.md)** - Détails exhaustifs
- **[🔧 Corrections Effectuées](CORRECTIONS_EFFECTUEES.md)** - Technique

### 📊 Architecture et Système
- **[📊 État Réel du Système](ETAT_REEL_SYSTEME.md)** - Architecture détaillée
- **[📄 Résumé Final](RESUME_FINAL.md)** - Solution complète
- **[📖 Solution Journal](SOLUTION_JOURNAL.md)** - Service de journal
- **[📚 Service Journal](docs/JOURNAL_SERVICE.md)** - Guide complet
- **[🧠 Reprise Intelligente](docs/SMART_SESSION_RESUME.md)** - Auto-sync des sessions ✨ NOUVEAU
- **[📊 Poids Structurels](GUIDE_POIDS_STRUCTURELS.md)** - Statistiques pondérées ✨ NOUVEAU

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

### Poids Structurels ✨ NOUVEAU
- Calcul des cardinalités par univers (Mundo: 544, Fruity: 435, etc.)
- Probabilités basées sur la taille réelle de chaque élément
- Gaps attendus calculés mathématiquement
- Scores normalisés pour comparaisons équitables
- Prédictions pondérées par la structure

### Gestion de Sessions Intelligente ✨ NOUVEAU
- Reprise automatique de session avec auto-synchronisation
- Chargement intelligent des loteries selon le programme
- Respect automatique des dates attribuées
- Création automatique des tirages manquants
- Réalignement calendaire des dates futures
- Génération de matrices Katula dynamiques
- Analyse des formes et structures
- Prédictions basées sur les patterns historiques

### API Endpoints
- `/api/katula-matrix` - Génération de matrices
- `/api/universe` - Informations sur les univers
- `/api/analysis` - Services d'analyse
- `/api/combinations` - Gestion des combinaisons
- `/api/journal` - Journal statistique avec validation BD

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

# Test du service de journal
python test_journal_service.py
```

## 📈 Développement

### Structure des Services
- **KatulaService**: Logique principale Katula
- **AnalysisService**: Services d'analyse
- **CombinationService**: Gestion des combinaisons
- **JournalService**: Journal statistique avec validation BD
- **StructuralWeightService**: Poids structurels et cardinalités ✨ NOUVEAU
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

### Version 2.0.5 (Actuel) ✨ NOUVEAU
- 🍓 **Dénominations Multiples**: Support complet slash (rainbow 6/rainbow 9)
- ✅ Endpoint `/api/formes/real/{universe}/all` corrigé
- ✅ Affichage adaptatif frontend (2, 3, 4+ dénominations)
- 🌍 **UX Univers Sélectionné**: Bandeau coloré avec icône dynamique
- ✅ Atténuation chips non sélectionnés (opacity 0.6)
- ✅ Surbrillance chip actif (bordure bleue, zoom)
- ✅ Affichage nombre de formes par univers
- 📚 Documentation: `ETAT_APPLICATION_2025.md`
- 🪧 Scripts: `update_github.bat` et `update_github.sh`

### Version 2.0.4 (Actuel) ✨ NOUVEAU
- 📊 **Poids Structurels**: Intégration des cardinalités naturelles
- ✅ Calcul automatique des probabilités par univers
- ✅ Gaps attendus basés sur la structure réelle
- ✅ Scores normalisés pour comparaisons équitables
- ✅ API complète pour poids structurels
- 📚 Documentation: `docs/STRUCTURAL_WEIGHTS_SPEC.md`
- 📚 Guide: `GUIDE_POIDS_STRUCTURELS.md`
- 🧪 Script de test: `backend/test_structural_weights.py`

### Version 2.0.3
- 🧠 **Reprise Intelligente de Session**: Auto-synchronisation lors de l'activation
- ✅ Chargement automatique des loteries selon le programme
- ✅ Respect automatique des dates attribuées
- ✅ Création automatique des tirages manquants
- ✅ Réalignement calendaire intelligent
- 📚 Documentation: `docs/SMART_SESSION_RESUME.md`
- 🧪 Script de test: `backend/test_smart_session_resume.py`

### Version 2.0.2
- ✨ **JournalServiceV2**: Service de journal statistique avec PostgreSQL
- ✅ Récupération des VRAIES données depuis PostgreSQL `katooling_main_system`
- ✅ Validation d'univers pour les tirages
- ✅ API endpoints pour génération de journaux
- ✅ Tests automatiques avec vraies données
- 📚 Documentation: `ETAT_REEL_SYSTEME.md` et `RESUME_FINAL.md`

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

## 📚 Documentation Supplémentaire

- [🎯 Résumé Final](RESUME_FINAL.md) - **COMMENCEZ ICI** - Résumé de la solution
- [📊 État Réel du Système](ETAT_REEL_SYSTEME.md) - Détails techniques complets
- [🧠 Reprise Intelligente](docs/SMART_SESSION_RESUME.md) - Auto-sync des sessions
- [📊 Poids Structurels](GUIDE_POIDS_STRUCTURELS.md) - **NOUVEAU** - Statistiques pondérées
- [Service de Journal Statistique](docs/JOURNAL_SERVICE.md) - Guide complet du JournalService
- [Solution Journal](SOLUTION_JOURNAL.md) - Résolution du problème de validation BD

## 📞 Support

Pour toute question ou support technique, contactez l'équipe de développement.

---

**Version**: 2.0.5  
**Dernière mise à jour**: Janvier 2025  
**Statut**: En développement actif