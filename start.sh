#!/bin/bash

echo "🚀 Démarrage d'EazzyCalculator..."
echo ""
echo "📁 Dossier de travail: $(pwd)"
echo "👤 Utilisateur Git: ciano228"
echo "📧 Email: brightmc33@gmail.com"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    echo "💡 Installez Python3 avec votre gestionnaire de paquets"
    exit 1
fi

echo "✅ Python3 détecté"
echo ""

# Créer le dossier data s'il n'existe pas
if [ ! -d "backend/data" ]; then
    echo "📁 Création du dossier backend/data..."
    mkdir -p backend/data
fi

# Démarrer le serveur intégré
echo "🌐 Démarrage du serveur intégré..."
echo "🔗 Interface: http://localhost:8000/katula-dynamic.html"
echo "📊 API: http://localhost:8000/docs"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python3 integrated_server.py