import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# URI de connexion Supabase (via le Connection Pooler)
DATABASE_URL = "postgresql://postgres.aiiwawdgrlhicatqtrza:MBs91033344@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"


def load_to_supabase(month: str = None) -> None:
    """
    Lit le fichier Parquet local depuis data/raw/ et le charge
    par lots optimisés dans la table PostgreSQL 'raw_yellow_trips' sur Supabase.
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    file_path = Path(f"data/raw/yellow_tripdata_{month}.parquet")

    if not file_path.exists():
        logging.warning(f"Fichier local introuvable : {file_path}")
        return

    try:
        logging.info(f"Lecture de {file_path.name}...")
        df = pd.read_parquet(file_path)
        
        logging.info(f"Chargement de {file_path.name} vers Supabase...")
        engine = create_engine(DATABASE_URL)
        
        # Envoi par lots de 5000 lignes pour un équilibre parfait entre vitesse et stabilité réseau
        df.to_sql(
            "raw_yellow_trips", 
            engine, 
            if_exists="append", 
            index=False,
            method="multi",
            chunksize=1000
        )
        
        logging.info(f"Fichier {file_path.name} chargé avec succès dans Supabase !")

    except Exception as e:
        logging.error(f"ERREUR lors du chargement de {file_path.name} : {str(e)}")


if __name__ == "__main__":
    months_to_load = ["2026-01", "2026-02", "2026-03"]
    
    for m in months_to_load:
        load_to_supabase(m)