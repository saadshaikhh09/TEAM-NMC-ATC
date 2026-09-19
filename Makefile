.PHONY: db api web reset seed test

db:
	docker compose up -d

reset:
	docker compose down -v && docker compose up -d
	@echo "Waiting for postgres..." && sleep 6
	@echo "Database reset with schema + seed."

api:
	cd api && uvicorn main:app --reload --port 8000

web:
	cd web && npm run dev

seed:
	docker compose exec -T db psql -U concierge -d concierge < db/seed.sql

test:
	cd api && python -m pytest tests -q
