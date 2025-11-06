#!/usr/bin/env python3
"""
Script pour créer les tables d'univers avec des données de test
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.connection import DATABASE_URL
import random
from datetime import datetime, timedelta

def create_universe_table(engine, universe_name):
    """Crée une table d'univers avec des données de test"""
    
    print(f"🏗️ Création de la table {universe_name}...")
    
    # Créer la table
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {universe_name} (
        id SERIAL PRIMARY KEY,
        combination_id INTEGER,
        denomination VARCHAR(100),
        forme VARCHAR(50),
        chip VARCHAR(20),
        tome VARCHAR(20),
        granque_name VARCHAR(10),
        parite VARCHAR(10),
        unidos VARCHAR(50),
        engine VARCHAR(50),
        beastie VARCHAR(50),
        date_tirage DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print(f"✅ Table {universe_name} créée")
        
        # Générer des données de test
        generate_test_data(conn, universe_name)

def generate_test_data(conn, universe_name):
    """Génère des données de test pour une table d'univers"""
    
    print(f"📊 Génération de données de test pour {universe_name}...")
    
    # Listes de valeurs possibles
    formes = ['carre', 'triangle', 'cercle', 'rectangle', 'carre-triangle', 'cercle-rectangle']
    granques = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6']
    tomes = ['tome1', 'tome2', 'tome3', 'tome4']
    parites = ['pair', 'impair']
    
    # Noms thématiques par univers
    denomination_themes = {
        'fruity': ['apple', 'banana', 'orange', 'grape', 'cherry', 'lemon', 'peach', 'berry'],
        'mundo': ['world', 'earth', 'planet', 'globe', 'universe', 'cosmos', 'space', 'star'],
        'trigga': ['fire', 'water', 'earth', 'air', 'lightning', 'ice', 'shadow', 'light'],
        'roaster': ['coffee', 'bean', 'roast', 'brew', 'espresso', 'latte', 'mocha', 'cappuccino'],
        'sunshine': ['sun', 'ray', 'bright', 'golden', 'warm', 'light', 'dawn', 'sunset']
    }
    
    theme = denomination_themes.get(universe_name, ['item', 'object', 'element', 'thing'])
    
    # Générer 500 enregistrements de test
    records = []
    start_date = datetime(2020, 1, 1)
    
    for i in range(500):
        # Date aléatoire entre 2020 et 2024
        random_days = random.randint(0, 1460)  # 4 ans * 365 jours
        date_tirage = start_date + timedelta(days=random_days)
        
        # Chip aléatoire (1-48)
        chip_num = random.randint(1, 48)
        
        # Dénomination thématique
        base_name = random.choice(theme)
        denomination = f"{base_name} {random.randint(1, 20)}"
        
        record = {
            'combination_id': i + 1,
            'denomination': denomination,
            'forme': random.choice(formes),
            'chip': f'chip{chip_num}',
            'tome': random.choice(tomes),
            'granque_name': random.choice(granques),
            'parite': random.choice(parites),
            'unidos': f"unidos_{random.randint(1, 10)}",
            'engine': f"engine_{random.randint(1, 5)}",
            'beastie': f"beastie_{random.randint(1, 8)}",
            'date_tirage': date_tirage.strftime('%Y-%m-%d')
        }
        
        records.append(record)
    
    # Insérer les données par batch
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        values_list = []
        for record in batch:
            values = f"({record['combination_id']}, '{record['denomination']}', '{record['forme']}', '{record['chip']}', '{record['tome']}', '{record['granque_name']}', '{record['parite']}', '{record['unidos']}', '{record['engine']}', '{record['beastie']}', '{record['date_tirage']}')"
            values_list.append(values)
        
        insert_sql = f"""
        INSERT INTO {universe_name} 
        (combination_id, denomination, forme, chip, tome, granque_name, parite, unidos, engine, beastie, date_tirage)
        VALUES {', '.join(values_list)}
        """
        
        conn.execute(text(insert_sql))
        conn.commit()
    
    print(f"✅ {len(records)} enregistrements insérés dans {universe_name}")

def main():
    """Fonction principale"""
    print("🚀 Création des tables d'univers...")
    
    # Connexion à la base de données
    engine = create_engine(DATABASE_URL)
    
    # Liste des univers à créer
    universes = ['fruity', 'mundo', 'trigga', 'roaster', 'sunshine']
    
    for universe in universes:
        try:
            create_universe_table(engine, universe)
            print(f"🎉 {universe} créé avec succès !\n")
        except Exception as e:
            print(f"❌ Erreur création {universe}: {e}\n")
    
    print("✅ Création des tables terminée !")
    print("\n🔧 Pour tester :")
    print("python test_simple_temporal.py")

if __name__ == "__main__":
    main()