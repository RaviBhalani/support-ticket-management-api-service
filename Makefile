ENV ?= local

.PHONY: help run migration upgrade downgrade

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

run: ## Tear down and re    build Docker services (usage: make run ENV=local)
	docker compose -f docker-compose.$(ENV).yaml --env-file .envs/$(ENV)/api.env down
	docker compose -f docker-compose.$(ENV).yaml --env-file .envs/$(ENV)/api.env up -d --build

migration: ## Generate a migration (usage: make migration msg="add users table")
	@test -n "$(msg)" || (echo "Error: msg is required. Usage: make migration msg=\"your message\"" && exit 1)
	docker compose -f docker-compose.$(ENV).yaml exec server alembic revision --autogenerate -m "$(msg)"

upgrade: ## Apply all pending migrations (usage: make upgrade)
	docker compose -f docker-compose.$(ENV).yaml exec server alembic upgrade head

downgrade: ## Roll back the last migration (usage: make downgrade)
	docker compose -f docker-compose.$(ENV).yaml exec server alembic downgrade -1
