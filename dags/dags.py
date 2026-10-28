from datetime import datetime, timedelta
from airflow.decorators import dag
from airflow.models.baseoperator import chain
from tasks import dataset, transformation_dbt

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='nyc_taxi_pipeline',
    default_args=default_args,
    description='Pipeline NYC Yellow Taxi modulaire',
    schedule='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['dbt', 'NYC taxi', 'snowflake'],
)
def nyc_taxi_pipeline():

    # Instanciation des groupes
    ingestion_task_group = dataset()
    dbt_task_group = transformation_dbt()

    chain(
        ingestion_task_group,
        dbt_task_group
    )


nyc_taxi_pipeline()