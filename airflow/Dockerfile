FROM apache/airflow:3.3.2-python3.12
# dbt est installé dans un environnement séparé pour éviter les conflits de dépendances avec Airflow
RUN python -m venv /opt/airflow/dbt-venv \
 && /opt/airflow/dbt-venv/bin/pip install --no-cache-dir dbt-core==1.8.9 dbt-postgres==1.8.2
