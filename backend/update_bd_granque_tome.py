#!/usr/bin/env python3
"""
Script pour mettre à jour la base de données avec les colonnes manquantes
et ajouter les univers complets
"""
import os
import psycopg2
from dotenv import load_dotenv
import random

load_dotenv()

def update_database():
    """Mettre à jour la base de données avec les colonnes et univers manquants"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        
        cursor = conn.cursor()
        
        print("=== MISE À JOUR BASE DE DONNÉES ===\n")
        
        # 1. Ajouter les colonnes manquantes à table_de_katula
        print("1. Ajout des colonnes manquantes...")
        
        # Vérifier si granque_name existe
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' AND column_name = 'granque_name'
        """)
        
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE table_de_katula ADD COLUMN granque_name VARCHAR(100)")
            print("   [OK] Colonne granque_name ajoutee")
        else:
            print("   [OK] Colonne granque_name existe deja")
        
        # Vérifier si tome existe
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' AND column_name = 'tome'
        """)
        
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE table_de_katula ADD COLUMN tome VARCHAR(50)")
            print("   [OK] Colonne tome ajoutee")
        else:
            print("   [OK] Colonne tome existe deja")
        
        # 2. Ajouter les colonnes manquantes à combinations
        print("\n2. Mise à jour table combinations...")
        
        # Vérifier si granque_name existe dans combinations
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'combinations' AND column_name = 'granque_name'
        """)
        
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE combinations ADD COLUMN granque_name VARCHAR(100)")
            print("   [OK] Colonne granque_name ajoutee a combinations")
        
        # Vérifier si tome existe dans combinations
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'combinations' AND column_name = 'tome'
        """)
        
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE combinations ADD COLUMN tome VARCHAR(50)")
            print("   [OK] Colonne tome ajoutee a combinations")
        
        # 3. Ajouter les univers manquants
        print("\n3. Ajout des univers manquants...")
        
        univers_complets = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        
        # Vérifier les univers existants
        cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
        univers_existants = [u[0] for u in cursor.fetchall()]
        print(f"   Univers existants: {univers_existants}")
        
        # Ajouter les univers manquants
        univers_manquants = [u for u in univers_complets if u not in univers_existants]
        print(f"   Univers a ajouter: {univers_manquants}")
        
        # Données de base pour chaque univers
        formes = ['triangle', 'carre', 'rectangle', 'losange', 'cercle']
        denominations_base = ['spoon', 'blade', 'house', 'table', 'rainbow', 'scissors', 'crown', 'star']
        tomes = ['tome1', 'tome2', 'tome3', 'tome4', 'tome5']
        granque_names = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta']
        
        for univers in univers_manquants:
            print(f"\n   Ajout de l'univers {univers}...")
            
            # Générer 30-40 entrées par univers
            nb_entrees = random.randint(30, 40)
            
            for i in range(nb_entrees):
                ligne = f"L{random.randint(1, 8)}"
                colonne = f"C{random.randint(1, 6)}"
                petique = f"q{random.randint(1, 4)}"
                chip = f"chip{random.randint(1, 48)}"
                forme = random.choice(formes)
                denomination = f"{random.choice(denominations_base)} {random.randint(1, 9)}"
                tome = random.choice(tomes)
                granque_name = f"{random.choice(granque_names)}-{random.randint(1, 99)}"
                
                cursor.execute("""
                    INSERT INTO table_de_katula 
                    (univers, ligne, colonne, petique, chip, forme, denomination, tome, granque_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (univers, ligne, colonne, petique, chip, forme, denomination, tome, granque_name))
            
            print(f"     [OK] {nb_entrees} entrees ajoutees pour {univers}")
        
        # 4. Mettre à jour les données existantes avec granque_name et tome
        print("\n4. Mise à jour des données existantes...")
        
        cursor.execute("SELECT chip_id, univers, denomination FROM table_de_katula WHERE granque_name IS NULL")
        lignes_a_mettre_a_jour = cursor.fetchall()
        
        for chip_id, univers, denomination in lignes_a_mettre_a_jour:
            tome = random.choice(tomes)
            granque_name = f"{random.choice(granque_names)}-{random.randint(1, 99)}"
            
            cursor.execute("""
                UPDATE table_de_katula 
                SET tome = %s, granque_name = %s 
                WHERE chip_id = %s
            """, (tome, granque_name, chip_id))
        
        print(f"   [OK] {len(lignes_a_mettre_a_jour)} lignes mises a jour")
        
        # 5. Vérification finale
        print("\n5. Vérification finale...")
        
        cursor.execute("SELECT DISTINCT univers FROM table_de_katula ORDER BY univers")
        univers_finaux = [u[0] for u in cursor.fetchall()]
        print(f"   Univers disponibles: {univers_finaux}")
        
        cursor.execute("SELECT COUNT(*) FROM table_de_katula")
        total_lignes = cursor.fetchone()[0]
        print(f"   Total lignes: {total_lignes}")
        
        # Vérifier les colonnes
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'table_de_katula' 
            ORDER BY ordinal_position
        """)
        colonnes = [c[0] for c in cursor.fetchall()]
        print(f"   Colonnes disponibles: {colonnes}")
        
        # Échantillon par univers
        for univers in univers_finaux:
            cursor.execute("SELECT COUNT(*) FROM table_de_katula WHERE univers = %s", (univers,))
            count = cursor.fetchone()[0]
            print(f"   {univers}: {count} entrées")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n[SUCCESS] MISE A JOUR TERMINEE AVEC SUCCES!")
        print("\nLes 5 univers sont maintenant disponibles:")
        print("- mundo, fruity, trigga, roaster, sunshine")
        print("- Colonnes granque_name et tome ajoutées")
        print("- Table combinations mise à jour")
        
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")

if __name__ == "__main__":
    update_database()