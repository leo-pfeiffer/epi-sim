# setup
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -U setuptools wheel
	pip install -U -r requirements.txt -r app/requirements.txt

.PHONY: env
env:
	sh ./scripts/generate_dotenv.sh

# unit tests
.PHONY: test
test:
	pytest

# run without docker
.PHONY: run
run:
	python app/run.py

# docker-compose
.PHONY: build
build:
	docker-compose up --build -d
	docker-compose ps

.PHONY: up
up:
	docker-compose up -d
	docker-compose ps

.PHONY: down
down:
	docker-compose down
	docker-compose ps

.PHONY: bash
bash:
	docker-compose run --rm app bash

.PHONY: destroy
destroy:
	docker-compose down --volumes
	docker rmi $(docker images -a -q)
	docker-compose ps

.PHONY: restart
restart:
	docker-compose restart
	docker-compose ps
