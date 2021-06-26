# setup
.PHONY: generate-data-paths
generate-data-paths:
	sh ./data_processing/generate_data_paths.sh

# unit tests
.PHONY: test
test:
	pytest -p no:cacheprovider

.PHONY: test-cache
test-cache:
	pytest

# run without docker
.PHONY: run
run:
	python app/run.py

# docker compose
.PHONY: up
up:
	docker compose up -d
	make ps

.PHONY: down
down:
	docker compose down
	make ps

.PHONY: ps
ps:
	docker compose ps

.PHONY: bash
bash:
	docker compose run --rm app bash

.PHONY: destroy
destroy:
	docker compose down --volumes
	make ps

.PHONY: build
build:
	docker compose up --build -d
	make ps

.PHONY: restart
restart:
	docker compose restart
	make ps
