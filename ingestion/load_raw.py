import logging
import os
from pathlib import Path

import pandas as pd
from psycopg import sql
from sqlalchemy import URL, create_engine, inspect


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parents[1]
FILE_PATH = PROJECT_DIR / "data/raw/yellow_tripdata_2026-01.parquet"

SCHEMA = "public"
TABLE = "raw_yellow_trips"
BATCH_SIZE = 50_000


def copy_to_postgres(table, connection, keys, data_iter):
    """Envoie un lot de données vers PostgreSQL avec COPY."""
    statement = sql.SQL("COPY {} ({}) FROM STDIN").format(
        sql.Identifier(table.schema or SCHEMA, table.name),
        sql.SQL(", ").join(sql.Identifier(key) for key in keys),
    )

    raw_connection = connection.connection.driver_connection
    count = 0

    with raw_connection.cursor() as cursor:
        with cursor.copy(statement) as copy:
            for row in data_iter:
                copy.write_row(row)
                count += 1

    logger.info("Lot envoyé : %s lignes", f"{count:,}")
    return count


def main():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(
            f"Fichier Parquet introuvable : {FILE_PATH}"
        )

    password = "npg_3cG6SkXJEzaY"

    if not password:
        raise RuntimeError(
            "La variable d'environnement PGPASSWORD est manquante."
        )

    url = URL.create(
        drivername="postgresql+psycopg",
        username="neondb_owner",
        password=password,
        host=(
            "ep-green-water-b9l27axr"
            ".c-7.eu-central-1.aws.neon.tech"
        ),
        port=5432,
        database="neondb",
        query={
            "sslmode": "require",
            "connect_timeout": "30",
        },
    )

    engine = create_engine(url)

    try:
        with engine.connect() as connection:
            if inspect(connection).has_table(TABLE, schema=SCHEMA):
                raise RuntimeError(
                    f"La table {SCHEMA}.{TABLE} existe déjà. "
                    "Chargement arrêté pour éviter les doublons "
                    "ou le remplacement des données."
                )

        logger.info("Lecture : %s", FILE_PATH.name)
        df = pd.read_parquet(FILE_PATH)

        if df.empty:
            raise RuntimeError("Le fichier Parquet ne contient aucune ligne.")

        logger.info(
            "Début du chargement : %s lignes",
            f"{len(df):,}",
        )

        with engine.begin() as connection:
            df.to_sql(
                name=TABLE,
                con=connection,
                schema=SCHEMA,
                if_exists="fail",
                index=False,
                chunksize=BATCH_SIZE,
                method=copy_to_postgres,
            )

            loaded_rows = connection.exec_driver_sql(
                'SELECT COUNT(*) FROM "public"."raw_yellow_trips"'
            ).scalar_one()

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Nombre de lignes incohérent : "
                    f"{len(df):,} attendues, "
                    f"{loaded_rows:,} chargées."
                )

        logger.info(
            "Chargement validé : %s lignes dans %s.%s",
            f"{loaded_rows:,}",
            SCHEMA,
            TABLE,
        )

        with engine.connect() as connection:
            database_size = connection.exec_driver_sql("""
                SELECT pg_size_pretty(
                    pg_database_size(current_database())
                )
            """).scalar_one()

        logger.info("Taille actuelle de la base : %s", database_size)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()