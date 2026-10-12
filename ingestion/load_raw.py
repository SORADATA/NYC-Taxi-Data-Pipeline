import duckdb

con = duckdb.connect("taxi.duckdb")
con.sql("""
    CREATE OR REPLACE TABLE raw_trips AS
    SELECT * FROM read_parquet('data/raw/yellow_tripdata_*.parquet')
""")
print(con.sql("SELECT COUNT(*) FROM raw_trips").fetchone())