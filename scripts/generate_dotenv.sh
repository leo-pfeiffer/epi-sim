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
  cat ./scripts/sample.env > .env
else
  echo "  >> [exists] .env"
fi
