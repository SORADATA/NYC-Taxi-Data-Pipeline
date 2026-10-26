import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def load_to_snowflake_database():
    # Récupération des variables d'environnement avec préfixe DBT_
    user = os.getenv("DBT_SNOWFLAKE_USER")
    password = os.getenv("DBT_SNOWFLAKE_PASSWORD")
    account = os.getenv("DBT_SNOWFLAKE_ACCOUNT")
    role = os.getenv("DBT_SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    database = os.getenv("DBT_SNOWFLAKE_DATABASE", "NYC_TAXI_DB")
    warehouse = os.getenv("DBT_SNOWFLAKE_WAREHOUSE", "NYC_TAXI_WH")

    if not password:
        raise ValueError("Erreur : La variable DBT_SNOWFLAKE_PASSWORD n'est pas définie !")

    print("Connexion à Snowflake en cours...")
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        role=role,
        warehouse=warehouse,
        database=database,
        schema="RAW"
    )

    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE NYC_TAXI_WH;")

        # Exécution du COPY INTO
        sql_query = """
            COPY INTO RAW_YELLOW_TRIPS
            FROM @NYC_TAXI_LANDING/yellow/2026-01/yellow_tripdata_2026-01.parquet
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

        """
        cursor.execute(sql_query)
        print("Données chargées avec succès dans RAW_YELLOW_TRIPS !")

    except Exception as e:
        print(f"Erreur lors du chargement : {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_to_snowflake_database()
