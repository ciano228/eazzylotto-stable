from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connexion réussie !")
except Exception as e:
    print(f"Erreur de connexion : {e}")