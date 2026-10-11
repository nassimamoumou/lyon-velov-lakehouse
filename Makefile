up:        ## démarre PostgreSQL et la collecte
	docker compose up -d --build
down:      ## arrête tout
	docker compose down
logs:      ## affiche les journaux de la collecte
	docker compose logs -f ingestion
test:      ## lance les tests
	python -m pytest -q
psql:      ## ouvre une console SQL
	docker compose exec postgres psql -U velov -d velov
