#!/bin/bash
set -euo pipefail

# make sure this is run from project root
expected_path=./scripts/generate_dotenv.sh
actual_path=$0

if [[ "$expected_path" != "$actual_path" ]]; then
  echo "Please run me from the project root" >&2
  exit 1
fi

# check if .env exists
if [[ ! -f .env ]] ; then
  echo "  >> [add] .env"
  cat ./scripts/ports.env > .env
  echo >> .env
  cat ./scripts/github.env >> .env
else
  echo "  >> [exists] .env"
fi

# check if app.env exists
if [[ ! -f ./app/app.env ]] ; then
  echo "  >> [add] app.env"
  cat ./scripts/github.env > ./app/app.env
else
  echo "  >> [exists] app.env"
fi
