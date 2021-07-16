## SETUP ========================

# install pip requirements
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -U setuptools wheel
	pip install -U -r requirements.txt -r app/requirements.txt

# generate .env and app.env files
.PHONY: env
env:
	sh ./scripts/generate_dotenv.sh

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

# build with docker-compose
.PHONY: build
build:
	make env
	docker-compose up --build -d
	docker-compose ps

# start existing container
.PHONY: up
up:
	docker-compose up -d
	docker-compose ps

# stop running container
.PHONY: down
down:
	docker-compose down
	docker-compose ps

# start bash session inside container
.PHONY: bash
bash:
	docker-compose run --rm app bash

# shut down containers, remove volumes, remove images - DESTRUCTIVE !
.PHONY: destroy
destroy:
	docker-compose down --volumes
	if [ ! -z "$(shell docker images -a -q)" ]; then \
		docker rmi $(shell docker images -a -q); \
	fi
	docker-compose ps

# restart container
.PHONY: restart
restart:
	docker-compose restart
	docker-compose ps
