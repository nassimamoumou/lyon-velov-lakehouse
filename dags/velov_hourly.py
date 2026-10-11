"""Chaque heure : collecte de la météo, puis reconstruction des tables d'analyse avec dbt."""
from datetime import datetime, timedelta

import os

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from velov_common import load_weather

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
DBT_BIN = os.getenv("DBT_BIN", "/opt/airflow/dbt-venv/bin/dbt")
DBT_BUILD = (
    "export DBT_TARGET_PATH=/tmp/dbt-target DBT_LOG_PATH=/tmp/dbt-logs && "
    f"cd {DBT_PROJECT_DIR} && {DBT_BIN} build --profiles-dir ."
)

with DAG(
    dag_id="velov_hourly",
    description="Météo horaire puis dbt build",
    start_date=datetime(2026, 10, 1),
    schedule="5 * * * *",
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["velov"],
) as dag:
    weather = PythonOperator(task_id="load_weather", python_callable=load_weather)
    dbt_build = BashOperator(task_id="dbt_build", bash_command=DBT_BUILD)

    weather >> dbt_build
