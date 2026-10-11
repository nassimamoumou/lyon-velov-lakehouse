up:        ## démarre toute la plateforme
	docker compose up -d --build
down:      ## arrête tout
	docker compose down
logs:      ## journaux de la collecte
	docker compose logs -f ingestion
test:      ## tests Python
	python -m pytest -q
dbt-build: ## lance dbt à la main (modèles + tests)
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && /opt/airflow/dbt-venv/bin/dbt build --profiles-dir ."
psql:      ## console SQL
	docker compose exec postgres psql -U velov -d velov
