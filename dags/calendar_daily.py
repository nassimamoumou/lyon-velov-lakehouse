"""Chaque jour : mise à jour des jours fériés et des vacances scolaires de l'académie de Lyon."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from velov_common import load_public_holidays, load_school_holidays

with DAG(
    dag_id="calendar_daily",
    description="Jours fériés et vacances scolaires",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["velov"],
) as dag:
    PythonOperator(task_id="load_public_holidays", python_callable=load_public_holidays)
    PythonOperator(task_id="load_school_holidays", python_callable=load_school_holidays)
