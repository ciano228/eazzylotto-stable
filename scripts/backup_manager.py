#!/usr/bin/env python3
"""
Script de gestion des backups automatiques
"""
import subprocess
import sys
from datetime import datetime
import os

def create_backup(description="auto-backup"):
    """Créer un backup automatique avec timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    branch_name = f"backup/{description}-{timestamp}"
    
    try:
        # Créer la branche de backup
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        
        # Ajouter tous les fichiers
        subprocess.run(["git", "add", "."], check=True)
        
        # Commiter
        commit_msg = f"backup: {description} - {datetime.now().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        print(f"✅ Backup créé: {branch_name}")
        return branch_name
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur backup: {e}")
        return None

def restore_backup(backup_branch):
    """Restaurer un backup spécifique"""
    try:
        subprocess.run(["git", "checkout", backup_branch], check=True)
        print(f"✅ Backup restauré: {backup_branch}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur restauration: {e}")
        return False

def list_backups():
    """Lister tous les backups disponibles"""
    try:
        result = subprocess.run(
            ["git", "branch", "-a"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        backups = [
            line.strip().replace("* ", "").replace("remotes/origin/", "")
            for line in result.stdout.split("\n")
            if "backup/" in line
        ]
        
        print("📋 Backups disponibles:")
        for backup in backups:
            print(f"  - {backup}")
        
        return backups
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur listage: {e}")
        return []

def create_test_branch(feature_name):
    """Créer une branche de test sécurisée"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    branch_name = f"dev/test-{feature_name}-{timestamp}"
    
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"✅ Branche de test créée: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur création branche: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_manager.py backup [description]")
        print("  python backup_manager.py restore <branch_name>")
        print("  python backup_manager.py list")
        print("  python backup_manager.py test <feature_name>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        description = sys.argv[2] if len(sys.argv) > 2 else "manual"
        create_backup(description)
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Spécifiez le nom de la branche à restaurer")
            sys.exit(1)
        restore_backup(sys.argv[2])
    
    elif command == "list":
        list_backups()
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ Spécifiez le nom de la fonctionnalité à tester")
            sys.exit(1)
        create_test_branch(sys.argv[2])
    
    else:
        print(f"❌ Commande inconnue: {command}")