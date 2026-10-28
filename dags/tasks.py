from airflow.decorators import task_group
from airflow.sdk.bases.operator import chain
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from src.extract import main_extraction
from src.load import load_to_snowflake_database


@task_group(task_group_id="dataset_ingestion")
def dataset():
    download = PythonOperator(
        task_id="download_data",
        python_callable=main_extraction,
    )
    load_to_snowflake = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_to_snowflake_database
    )

    chain(
        download,
        load_to_snowflake,
    )


@task_group(task_group_id="dbt_transformation")
def transformation_dbt():
    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='dbt seed --project-dir /opt/airflow/dbt/nyc_taxi'
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir /opt/airflow/dbt/nyc_taxi'
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --project-dir /opt/airflow/dbt/nyc_taxi'
    )

    chain(
        dbt_seed,
        dbt_run,
        dbt_test,
    )
