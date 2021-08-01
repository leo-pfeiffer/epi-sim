ENV=prod
DOCK_COMP = "./app/docker-compose.$(ENV).yml"
CLEAR_DATA = ./app/app/app/data/clear_data.py


## SETUP ========================

.PHONY: requirements_lib
# Install pip requirements for lib only
requirements_lib:
	pip install -U -r lib/requirements.txt

.PHONY: requirements_app
# Install pip requirements for app only
requirements_app:
	pip install -U -r app/app/requirements.txt

.PHONY: requirements
# Install all pip requirements
requirements:
	pip install --upgrade pip
	pip install -U setuptools wheel
	make requirements_lib
	make requirements_app

.PHONY: env
# Generate .env files
env:
	sh ./setup/generate_dotenv.sh

.PHONY: setup
# Full setup of the project
setup:
	make env
	make requirements

.PHONY: setup_lib
# Setup of lib only
setup_lib:
	make env
	make requirements_lib

.PHONY: setup_app
# Setup of the project
setup_app:
	make env
	make requirements_app


## TESTING ========================

.PHONY: test
# Run all unit tests
test:
	pytest

.PHONY: test
# Run unit tests for app
test_app:
	pytest app/app/app/tests

.PHONY: test_lib
# Run unit tests for lib
test_lib:
	pytest lib/tests

## LIB SCRIPTS ====================

.PHONY: create_app_data
# Create data for web app from simulation results
create_app_data:
	python -m lib.experiments.utils.create_app_data

.PHONY: batch_upload_experiments
# Upload experiment results
batch_upload_experiments:
	python -m lib.experiments.utils.batch_upload_experiments


## WEB APP ========================

.PHONY: run
# Run web app with Flask dev server (dev only)
run:
	make env
	export FLASK_ENV=development; \
	python app/app/run.py

.PHONY: build
# Build web app with docker-compose
build:
	make env
	docker-compose -f $(DOCK_COMP) up --force-recreate --build -d
	docker image prune -f
	docker-compose -f $(DOCK_COMP) ps

.PHONY: up
# Start existing container 
up:
	docker-compose -f $(DOCK_COMP) up -d
	docker-compose -f $(DOCK_COMP) ps

.PHONY: down
# Stop running container 
down:
	docker-compose -f $(DOCK_COMP) down
	docker-compose -f $(DOCK_COMP) ps

.PHONY: logs
# Attach docker compose logs 
logs:
	docker-compose -f $(DOCK_COMP) logs --follow

.PHONY: bash
# Start bash inside container 
bash:
	docker-compose -f $(DOCK_COMP) run --rm app bash

.PHONY: restart
# Restart container 
restart:
	docker-compose -f $(DOCK_COMP) restart
	docker-compose -f $(DOCK_COMP) ps

.PHONY: clear-data
# Clear downloaded app data
clear-data:
	python $(CLEAR_DATA)


# ----- Usage -----

.PHONY: help
# Found here: https://stackoverflow.com/a/35730928/12168211
# Print available commands
help:
	@echo "=============================================================="
	@echo "Available Make commands ======================================"
	@echo "=============================================================="
	@echo "For Docker commands: default is ENV=prod; for dev set ENV=dev)"
	@echo "=============================================================="
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t