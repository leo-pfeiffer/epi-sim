ENV="prod"
DOCK_COMP = "./app/docker-compose.$(ENV).yml"


## SETUP ========================

# install pip requirements
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -U setuptools wheel
	pip install -U -r lib/requirements.txt -r app/app/requirements.txt

# generate .env files
.PHONY: env
env:
	sh ./setup/generate_dotenv.sh

# full setup
.PHONY: setup
setup:
	make env
	make requirements


## TESTING ========================

# run unit tests
.PHONY: test
test:
	pytest


## WEB APP ========================

# run without docker
.PHONY: run
run:
	make env
	python app/run.py

# build with docker-compose -f $(DOCK_COMP)
.PHONY: build
build:
	make env
	docker-compose -f $(DOCK_COMP) up --build -d
	docker-compose -f $(DOCK_COMP) ps

# start existing container
.PHONY: up
up:
	docker-compose -f $(DOCK_COMP) up -d
	docker-compose -f $(DOCK_COMP) ps

# stop running container
.PHONY: down
down:
	docker-compose -f $(DOCK_COMP) down
	docker-compose -f $(DOCK_COMP) ps

# show docker compose logs
.PHONY: logs
logs:
	docker-compose -f $(DOCK_COMP) logs --follow

# start bash session inside container
.PHONY: bash
bash:
	docker-compose -f $(DOCK_COMP) run --rm app bash

# shut down containers, remove volumes, remove images - DESTRUCTIVE !
.PHONY: destroy
destroy:
	docker-compose -f $(DOCK_COMP) down --volumes
	if [ ! -z "$(shell docker images -a -q)" ]; then \
		docker rmi $(shell docker images -a -q); \
	fi
	docker-compose -f $(DOCK_COMP) ps

# restart container
    .PHONY: restart
restart:
	docker-compose -f $(DOCK_COMP) restart
	docker-compose -f $(DOCK_COMP) ps

# ----- Usage -----

define HELP
==============================================

    make help           Print available commands

==============================================
SETUP ========================================

   make requirements    install pip requirements
   make env             generate .env files
   make setup           make a full setup

==============================================
TESTING ======================================

   make test            run unit tests

==============================================
WEB APP ======================================

   FLASK (dev only)
      make run             (dev only) run app with Flask

   DOCKER (defaults to prod, for dev specify ENV=dev with the command)
      make build           build app with docker-compose
      make up              start existing container
      make down            stop running container
      make logs            attach docker-compose logs
      make bash            enter running container and start bash session
      make destroy         shut down and destroy container (remove volumes & images)
      make restart         restart container

==============================================
endef
export HELP

help:
	@echo "$$HELP"
