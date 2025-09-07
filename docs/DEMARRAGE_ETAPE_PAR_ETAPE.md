# 🚀 Guide de Démarrage Étape par Étape - EazzyCalculator

## ⚠️ Problème Identifié

Vous obtenez l'erreur "No such file or directory" car vous essayez de lancer les fichiers depuis le mauvais répertoire.

## ✅ Solutions Disponibles

### **Option 1 : Script PowerShell (Recommandé)**
1. Ouvrez PowerShell en tant qu'administrateur
2. Naviguez vers votre projet : `cd C:\Users\User\eazzycalculator`
3. Exécutez : `.\start_servers.ps1`

### **Option 2 : Démarrage Manuel Détaillé**

#### **Étape 1 : Vérifier la Structure**
```powershell
# Dans PowerShell, vérifiez que vous êtes dans le bon répertoire
cd C:\Users\User\eazzycalculator
ls
```

Vous devriez voir :
- `backend/` (dossier)
- `frontend/` (dossier)
- `start_servers.ps1` (fichier)

#### **Étape 2 : Démarrer le Backend**
```powershell
# Terminal 1 - Backend
cd C:\Users\User\eazzycalculator\backend
python main_complete.py
```

**Résultat attendu :**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### **Étape 3 : Démarrer le Frontend (Nouveau Terminal)**
```powershell
# Terminal 2 - Frontend (nouvelle fenêtre PowerShell)
cd C:\Users\User\eazzycalculator\frontend
python server.py
```

**Résultat attendu :**
```
📁 Répertoire de travail: C:\Users\User\eazzycalculator\frontend
📄 Fichiers disponibles: [liste des fichiers]
🚀 Serveur frontend démarré sur http://localhost:8081
🎯 Katula Dynamique: http://localhost:8081/katula-dynamic.html
🧪 Test Simple: http://localhost:8081/test-simple.html
💡 Appuyez sur Ctrl+C pour arrêter
```

## 🔧 Vérification des Serveurs

### **Test du Backend**
```powershell
curl http://localhost:8000
```
**Résultat attendu :**
```json
{"message":"EazzyCalculator API is running","version":"1.0.0"}
```

### **Test du Frontend**
```powershell
curl http://localhost:8081
```
**Résultat attendu :** Page HTML du serveur frontend

## 🌐 Accès au Dashboard Fonctionnel

Une fois les serveurs démarrés, ouvrez votre navigateur :

- **Dashboard Principal** : http://localhost:8081/dashboard.html
- **Page d'Accueil** : http://localhost:8081/index.html
- **Workflow KATOOLING** : http://localhost:8081/katooling-workflow.html

## 🎯 Test des Fonctionnalités

Dans le dashboard, testez :

1. **Cliquez sur "Recherche & Données"** → Section interactive s'ouvre
2. **Cliquez sur "Analyse Temporelle"** → Bouton "Lancer l'Analyse" disponible
3. **Cliquez sur "Prédictions IA"** → Bouton "Générer Prédictions" disponible
4. **Cliquez sur "Résultats Gagnants"** → Données s'affichent automatiquement
5. **Cliquez sur "Workflow KATOOLING"** → Bouton "Exécuter Workflow" disponible

## ❓ Résolution des Problèmes

### **Erreur "No such file or directory"**
- **Cause** : Mauvais répertoire
- **Solution** : Utilisez `cd` pour naviguer vers le bon dossier

### **Erreur "Module not found"**
- **Cause** : Dépendances manquantes
- **Solution** : 
  ```powershell
  cd C:\Users\User\eazzycalculator\backend
  pip install -r requirements.txt
  ```

### **Port déjà utilisé**
- **Cause** : Autre service sur les ports 8000/8081
- **Solution** : Fermez les applications utilisant ces ports

### **PowerShell Execution Policy**
- **Cause** : Politique d'exécution restrictive
- **Solution** :
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 🎉 Résultat Final

Une fois tout configuré, vous aurez :
- ✅ Backend API fonctionnel sur le port 8000
- ✅ Frontend serveur fonctionnel sur le port 8081
- ✅ Dashboard entièrement interactif
- ✅ Toutes les composantes fonctionnelles

## 📞 Support

Si le problème persiste :
1. Vérifiez que Python est installé : `python --version`
2. Vérifiez que vous êtes dans le bon répertoire : `pwd`
3. Vérifiez que les fichiers existent : `ls backend/` et `ls frontend/`

**🚀 Votre application EazzyCalculator sera alors prête à être utilisée !** 