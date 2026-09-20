.PHONY: db api web site reset seed test dev

db:
	docker compose up -d

dev:
	./start.sh

reset:
	@if command -v docker >/dev/null 2>&1 && docker compose ps >/dev/null 2>&1; then \
		docker compose down -v && docker compose up -d && sleep 6; \
	else \
		psql -q -U concierge -d concierge -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" && \
		psql -q -U concierge -d concierge -f db/schema.sql && \
		psql -q -U concierge -d concierge -f db/seed.sql; \
	fi
	@for f in db/migrations/*.sql; do \
		[ -f "$$f" ] && echo "  applying $$f" && psql -q -U concierge -d concierge -f "$$f"; \
	done
	@psql -q -t -U concierge -d concierge -c "select count(*) from travellers;"
	@echo "Database reset with schema + seed + migrations."

api:
	cd api && .venv/bin/uvicorn main:app --reload --port 8000

# web/ is not a workspace: web/app and web/site are independent surfaces with
# their own package.json. `cd web && npm run dev` has no package.json to find.
web:
	cd web/app && npm run dev

site:
	cd web/site && npm run dev

seed:
	docker compose exec -T db psql -U concierge -d concierge < db/seed.sql

test:
	@psql -q -U concierge -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='concierge_test'" | grep -q 1 || createdb -U concierge concierge_test
	@psql -q -U concierge -d concierge_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@psql -q -U concierge -d concierge_test -f db/schema.sql
	@psql -q -U concierge -d concierge_test -f db/seed.sql
	@for f in db/migrations/*.sql; do [ -f "$$f" ] && psql -q -U concierge -d concierge_test -f "$$f"; done
	cd api && DATABASE_URL=postgresql://concierge:concierge@localhost:5432/concierge_test TESTING=true GEMINI_API_KEY= OPENAI_API_KEY= OPENROUTER_API_KEY= XKIRO_API_KEY= GROQ_API_KEY= GROQ_MODEL= .venv/bin/python -m pytest tests -q
reset-local:
	psql -U concierge -d concierge -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	psql -U concierge -d concierge -f db/schema.sql
	psql -U concierge -d concierge -f db/seed.sql
	@echo "Database reset with schema + seed."
