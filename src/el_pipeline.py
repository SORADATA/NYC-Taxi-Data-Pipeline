import dotenv
import os
from pathlib import Path
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

def extract_from_nyc():
    

def load_to_snowflake(file_path: Path):
    df = pd.read_parquet(file_path)
    df.columns = [c.upper() for c in df.columns]

    conn = snowflake.connector.connect(
        user=os.getenv("DBT_SNOWFLAKE_USER"),
        password=os.getenv("DBT_SNOWFLAKE_PASSWORD"),
        account=os.getenv("DBT_SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("DBT_SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("DBT_SNOWFLAKE_DATABASE", "NYC_TAXI_DB"),
        schema="PUBLIC",
        role=os.getenv("DBT_SNOWFLAKE_ROLE"),
    )
    try:
        ok, n_chunks, n_rows, _ = write_pandas(
            conn, df, table_name=TABLE,
            auto_create_table=True, use_logical_type=True,
        )
        logger.info("Chargé : %s lignes dans %s.%s", f"{n_rows:,}", SCHEMA, TABLE)
    finally:
        conn.close()