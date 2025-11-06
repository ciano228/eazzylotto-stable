#!/usr/bin/env python3
"""
Script pour mettre à jour la base de données avec les nouvelles colonnes
"""
from sqlalchemy import text
from app.database.connection import engine
import sys

def update_database():
    """Ajouter les nouvelles colonnes aux tables existantes"""
    
    try:
        with engine.connect() as connection:
            # Commencer une transaction
            trans = connection.begin()
            
            try:
                print("🔄 Mise à jour de la base de données...")
                
                # Vérifier si les tables existent
                result = connection.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('work_sessions', 'session_draws')
                """))
                
                existing_tables = [row[0] for row in result]
                print(f"📋 Tables existantes: {existing_tables}")
                
                # Créer les tables si elles n'existent pas
                if 'work_sessions' not in existing_tables:
                    print("📝 Création de la table work_sessions...")
                    connection.execute(text("""
                        CREATE TABLE work_sessions (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR NOT NULL,
                            description VARCHAR,
                            lottery_type VARCHAR NOT NULL,
                            numbers_per_draw INTEGER NOT NULL,
                            number_range_min INTEGER DEFAULT 1,
                            number_range_max INTEGER DEFAULT 90,
                            total_draws INTEGER NOT NULL,
                            current_draw INTEGER DEFAULT 1,
                            cycle_length INTEGER DEFAULT 7,
                            lottery_schedule JSON,
                            start_date TIMESTAMP NOT NULL,
                            is_active BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    print("🔧 Mise à jour de la table work_sessions...")
                    
                    # Ajouter les nouvelles colonnes si elles n'existent pas
                    columns_to_add = [
                        ("cycle_length", "INTEGER DEFAULT 7"),
                        ("lottery_schedule", "JSON"),
                        ("start_date", "TIMESTAMP")
                    ]
                    
                    for column_name, column_def in columns_to_add:
                        try:
                            connection.execute(text(f"""
                                ALTER TABLE work_sessions 
                                ADD COLUMN {column_name} {column_def}
                            """))
                            print(f"  ✅ Colonne {column_name} ajoutée")
                        except Exception as e:
                            if "already exists" in str(e).lower():
                                print(f"  ℹ️  Colonne {column_name} existe déjà")
                            else:
                                print(f"  ⚠️  Erreur pour {column_name}: {e}")
                
                # Créer ou mettre à jour la table session_draws
                if 'session_draws' not in existing_tables:
                    print("📝 Création de la table session_draws...")
                    connection.execute(text("""
                        CREATE TABLE session_draws (
                            id SERIAL PRIMARY KEY,
                            session_id INTEGER NOT NULL REFERENCES work_sessions(id),
                            draw_number INTEGER NOT NULL,
                            cycle_position INTEGER NOT NULL DEFAULT 0,
                            lottery_name VARCHAR NOT NULL,
                            draw_date TIMESTAMP NOT NULL,
                            winning_numbers JSON,
                            is_completed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    print("🔧 Mise à jour de la table session_draws...")
                    
                    # Ajouter la colonne cycle_position si elle n'existe pas
                    try:
                        connection.execute(text("""
                            ALTER TABLE session_draws 
                            ADD COLUMN cycle_position INTEGER DEFAULT 0
                        """))
                        print("  ✅ Colonne cycle_position ajoutée")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            print("  ℹ️  Colonne cycle_position existe déjà")
                        else:
                            print(f"  ⚠️  Erreur pour cycle_position: {e}")
                
                # Valider la transaction
                trans.commit()
                print("✅ Base de données mise à jour avec succès!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Erreur lors de la mise à jour: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Erreur de connexion à la base: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = update_database()
    sys.exit(0 if success else 1)