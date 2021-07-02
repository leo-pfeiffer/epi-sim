# setup
.PHONY: generate-data-paths
generate-data-paths:
	sh ./data_processing/generate_data_paths.sh

.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -r requirements.txt -r app/requirements.txt


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
