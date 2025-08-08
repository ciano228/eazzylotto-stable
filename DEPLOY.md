# 🚀 Guide de Déploiement GitHub

## 📋 Étapes pour Publier sur GitHub (ciano228)

### **1. Initialiser Git**
```bash
cd c:\Users\User\eazzycalculator
git init
git add .
git commit -m "🎯 Version stable EazzyLotto - Système KATOOLING"
```

### **2. Créer le Repository sur GitHub**
1. Aller sur https://github.com/ciano228
2. Cliquer "New repository"
3. Nom : `eazzylotto-stable`
4. Description : `🎯 EazzyLotto - Système de Prédiction Loto Intelligent avec méthode KATOOLING`
5. Public ✅
6. Ne pas initialiser avec README (on a déjà le nôtre)

### **3. Connecter et Pousser**
```bash
git remote add origin https://github.com/ciano228/eazzylotto-stable.git
git branch -M main
git push -u origin main
```

### **4. Configuration GitHub Pages (Optionnel)**
1. Settings → Pages
2. Source : Deploy from a branch
3. Branch : main / frontend
4. URL : https://ciano228.github.io/eazzylotto-stable/

## 🔧 Structure Repository

```
eazzylotto-stable/
├── README.md                 # Documentation principale
├── STABLE_VERSION.md         # Version verrouillée
├── DEPLOY.md                 # Ce guide
├── .gitignore               # Fichiers à ignorer
├── frontend/                # Application web
│   ├── index.html
│   ├── dashboard.html
│   └── assets/
├── backend/                 # API Python
│   ├── main.py
│   ├── requirements.txt
│   └── app/
└── docs/                    # Documentation
```

## 🏷️ Tags de Version

```bash
git tag -a v1.0.0 -m "🎯 Version stable initiale"
git push origin v1.0.0
```

## 🔒 Branches Protégées

- `main` : Version stable de production
- `develop` : Développement en cours
- `feature/*` : Nouvelles fonctionnalités

## 📊 Badges README

```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![License](https://img.shields.io/badge/license-proprietary-red)
```