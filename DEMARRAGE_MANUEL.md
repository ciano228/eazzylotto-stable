# 🚀 Guide de Démarrage Manuel - EazzyCalculator

## ⚠️ Problème Résolu

Si vous obtenez des erreurs comme "No such file or directory", c'est parce que vous essayez de lancer les serveurs depuis le mauvais répertoire.

## ✅ Solution Simple

### **Option 1 : Script Automatique (Recommandé)**
Double-cliquez sur le fichier `start_servers.bat` dans le répertoire racine de votre projet.

### **Option 2 : Démarrage Manuel**

#### **Étape 1 : Démarrer le Backend**
1. Ouvrez un terminal/PowerShell
2. Naviguez vers le dossier backend :
   ```bash
   cd C:\Users\User\eazzycalculator\backend
   ```
3. Lancez le serveur backend :
   ```bash
   python main_complete.py
   ```
4. Vous devriez voir : "INFO: Uvicorn running on http://0.0.0.0:8000"

#### **Étape 2 : Démarrer le Frontend (Nouveau Terminal)**
1. Ouvrez un **nouveau** terminal/PowerShell
2. Naviguez vers le dossier frontend :
   ```bash
   cd C:\Users\User\eazzycalculator\frontend
   ```
3. Lancez le serveur frontend :
   ```bash
   python server.py
   ```
4. Vous devriez voir : "🚀 Serveur frontend démarré sur http://localhost:8081"

## 🌐 Accès aux Pages

Une fois les serveurs démarrés :

- **Dashboard Fonctionnel** : http://localhost:8081/dashboard.html
- **Page d'Accueil** : http://localhost:8081/index.html
- **Workflow KATOOLING** : http://localhost:8081/katooling-workflow.html
- **Test API** : http://localhost:8081/test-katooling-workflow.html

## 🔧 Vérification

Pour vérifier que les serveurs fonctionnent :

```bash
# Test du backend
curl http://localhost:8000

# Test du frontend
curl http://localhost:8081
```

## ❓ Problèmes Courants

### **Erreur "No such file or directory"**
- **Cause** : Vous n'êtes pas dans le bon répertoire
- **Solution** : Utilisez `cd` pour naviguer vers le bon dossier

### **Port déjà utilisé**
- **Cause** : Un autre service utilise les ports 8000 ou 8081
- **Solution** : Fermez les applications qui utilisent ces ports

### **Module not found**
- **Cause** : Les dépendances ne sont pas installées
- **Solution** : Exécutez `pip install -r requirements.txt` dans le dossier backend

## 🎯 Test du Dashboard Fonctionnel

Une fois connecté au dashboard :

1. **Cliquez sur "Recherche & Données"** → Section interactive s'ouvre
2. **Cliquez sur "Analyse Temporelle"** → Bouton "Lancer l'Analyse" disponible
3. **Cliquez sur "Prédictions IA"** → Bouton "Générer Prédictions" disponible
4. **Cliquez sur "Résultats Gagnants"** → Données s'affichent automatiquement
5. **Cliquez sur "Workflow KATOOLING"** → Bouton "Exécuter Workflow" disponible

## 🎉 Résultat

Votre dashboard sera **100% fonctionnel** avec :
- ✅ Navigation interactive entre les sections
- ✅ Données en temps réel depuis l'API
- ✅ Actions pour tous les workflows
- ✅ Interface moderne et responsive

**🚀 Bonne utilisation de votre application EazzyCalculator !** 