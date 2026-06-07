# Makefile
# Role: developer entrypoints for mhtran-dash
# Description: thin wrappers over docker compose with dev/prod overlays.

SHELL := /bin/bash

COMPOSE          := docker compose
DEV_FILES        := -f docker-compose.yml -f docker-compose.dev.yml
PROD_FILES       := -f docker-compose.yml -f docker-compose.prod.yml
PROXMOX_FILES    := -f docker-compose.yml -f compose.prod.proxmox.yml

ALEMBIC       := $(COMPOSE) $(DEV_FILES) exec -T api uv run alembic

.PHONY: rasters rasters-one seed-substations seed-lines seed-all

UV := $(shell command -v uv 2>/dev/null || echo $(HOME)/.local/bin/uv)

PROJ_DB := $(shell find $(CURDIR)/scripts/.venv -name "proj.db" -path "*/rasterio/*" 2>/dev/null | head -1 | xargs dirname 2>/dev/null)

rasters:
	cd scripts && PROJ_DATA=$(PROJ_DB) $(UV) run python -m build_rasters all

rasters-one:
	@test -n "$(NAME)" || (echo "usage: make rasters-one NAME=lightning" && exit 1)
	cd scripts && PROJ_DATA=$(PROJ_DB) $(UV) run python -m build_rasters one $(NAME)

seed-substations:
	$(COMPOSE) $(DEV_FILES) exec -T api uv run python -m mhtran_api.cli seed substations

seed-lines:
	$(COMPOSE) $(DEV_FILES) exec -T api uv run python -m mhtran_api.cli seed lines

seed-all: seed-substations seed-lines

.PHONY: help \
        dev dev-build down logs ps web-dev \
        api-shell db-shell psql \
        health ready \
        migration migrate downgrade history current \
        prod prod-build prod-down \
        prod-proxmox prod-proxmox-build prod-proxmox-down \
        clean

help:
	@echo "mhtran-dash targets:"
	@echo ""
	@echo "Development (db + api only; run web separately via make web-dev):"
	@echo "  make dev                  start dev stack"
	@echo "  make dev-build            rebuild dev images and start"
	@echo "  make down                 stop dev stack"
	@echo "  make logs                 tail dev logs"
	@echo "  make ps                   list running services"
	@echo "  make web-dev              run Vite dev server (cd web && npm run dev)"
	@echo ""
	@echo "Shell / inspection:"
	@echo "  make api-shell            bash inside api container"
	@echo "  make db-shell             bash inside db container"
	@echo "  make psql                 psql into the db"
	@echo "  make health               curl /health"
	@echo "  make ready                curl /ready"
	@echo ""
	@echo "Database migrations:"
	@echo "  make migration MSG=\"...\"  autogenerate migration"
	@echo "  make migrate              apply to head"
	@echo "  make downgrade            revert one step"
	@echo "  make history / current    show migration state"
	@echo ""
	@echo "Data pipeline:"
	@echo "  make rasters              rebuild all 9 hazard rasters"
	@echo "  make rasters-one NAME=x   rebuild one raster"
	@echo "  make seed-substations     load substations from parquets"
	@echo "  make seed-lines           load transmission lines"
	@echo "  make seed-all             seed substations + lines"
	@echo ""
	@echo "Production — Proxmox (db + api, port \$$MHTRAN_PORT; web via GitHub Pages):"
	@echo "  make prod-proxmox         start full stack"
	@echo "  make prod-proxmox-build   rebuild images and start"
	@echo "  make prod-proxmox-down    stop"
	@echo ""
	@echo "  make clean                stop dev stack and remove volumes"

web-dev:
	cd web && npm run dev

dev:
	$(COMPOSE) $(DEV_FILES) up -d
	@$(MAKE) --no-print-directory ps

dev-build:
	$(COMPOSE) $(DEV_FILES) up -d --build
	@$(MAKE) --no-print-directory ps

down:
	$(COMPOSE) $(DEV_FILES) down

logs:
	$(COMPOSE) $(DEV_FILES) logs -f --tail=100

ps:
	$(COMPOSE) $(DEV_FILES) ps

api-shell:
	$(COMPOSE) $(DEV_FILES) exec api bash

db-shell:
	$(COMPOSE) $(DEV_FILES) exec db bash

psql:
	$(COMPOSE) $(DEV_FILES) exec db psql -U $${POSTGRES_USER:-mhtran} -d $${POSTGRES_DB:-mhtran}

health:
	@curl -fsS http://localhost:8035/health | python3 -m json.tool

ready:
	@curl -fsS http://localhost:8035/ready | python3 -m json.tool

migration:
	@test -n "$(MSG)" || (echo "usage: make migration MSG=\"description\"" && exit 1)
	$(ALEMBIC) revision --autogenerate -m "$(MSG)"

migrate:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

history:
	$(ALEMBIC) history

current:
	$(ALEMBIC) current

prod:
	$(COMPOSE) $(PROD_FILES) up -d
	@$(COMPOSE) $(PROD_FILES) ps

prod-build:
	$(COMPOSE) $(PROD_FILES) up -d --build
	@$(COMPOSE) $(PROD_FILES) ps

prod-down:
	$(COMPOSE) $(PROD_FILES) down

prod-proxmox:
	$(COMPOSE) $(PROXMOX_FILES) up -d
	@$(COMPOSE) $(PROXMOX_FILES) ps

prod-proxmox-build:
	$(COMPOSE) $(PROXMOX_FILES) up -d --build
	@$(COMPOSE) $(PROXMOX_FILES) ps

prod-proxmox-down:
	$(COMPOSE) $(PROXMOX_FILES) --profile web down

clean:
	$(COMPOSE) $(DEV_FILES) down -v --remove-orphans