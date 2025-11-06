# Instructions de Déploiement Git

## 📋 Étapes pour créer le dépôt GitHub

### 1. Créer le dépôt sur GitHub
1. Aller sur [GitHub](https://github.com)
2. Se connecter avec le compte `ciano228`
3. Cliquer sur "New repository" (bouton vert)
4. Nom du repository : `eazzycalculator`
5. Description : `Système d'analyse Katula - Version professionnelle pour prédiction loterie`
6. Choisir "Private" ou "Public" selon vos préférences
7. **NE PAS** cocher "Initialize with README" (nous avons déjà un README)
8. Cliquer "Create repository"

### 2. Lier le dépôt local au dépôt distant

```bash
# Ajouter l'origine distante
git remote add origin https://github.com/ciano228/eazzycalculator.git

# Vérifier la configuration
git remote -v

# Pousser vers GitHub
git push -u origin main
```

### 3. Commandes Git de base pour la suite

```bash
# Ajouter des modifications
git add .

# Faire un commit
git commit -m "Description des modifications"

# Pousser vers GitHub
git push

# Vérifier le statut
git status

# Voir l'historique
git log --oneline
```

## 🔧 Configuration du projet

### Variables d'environnement
1. Copier `.env.example` vers `.env` dans le dossier `backend/`
2. Modifier les valeurs selon votre environnement

### Démarrage rapide
```bash
# Démarrer le serveur intégré
python integrated_server.py

# Ou démarrer le backend seul
cd backend
python -m uvicorn main:app --reload --port 8000
```

## 📊 Structure du dépôt

```
eazzycalculator/
├── .gitignore              # Fichiers à ignorer
├── README.md               # Documentation principale
├── CHANGELOG.md            # Historique des versions
├── integrated_server.py    # Serveur intégré
├── backend/                # API FastAPI
├── frontend/               # Interface utilisateur
├── scripts/                # Scripts utilitaires
└── tests/                  # Tests automatisés
```

## 🚀 Prochaines étapes

1. **Créer le dépôt GitHub** avec les instructions ci-dessus
2. **Configurer les branches** :
   - `main` : version stable
   - `develop` : développement
   - `feature/*` : nouvelles fonctionnalités

3. **Configurer les workflows GitHub Actions** (optionnel)
4. **Inviter des collaborateurs** si nécessaire

## 📞 Support

En cas de problème :
1. Vérifier que Git est installé : `git --version`
2. Vérifier la configuration : `git config --list`
3. Vérifier les remotes : `git remote -v`

---

**Projet** : EazzyCalculator v2.0.0  
**Propriétaire** : ciano228  
**Email** : brightmc33@gmail.com