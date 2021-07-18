#!/bin/bash
set -eu pipefail

# make sure this is run from project root
expected_path=./setup/generate_dotenv.sh
actual_path=$0

if [ "$expected_path" != "$actual_path" ]; then
  echo "Please run me from the project root" >&2
  exit 1
fi

# check if ./lib/.env exists
if [ ! -f ./lib/.env ] ; then
  echo "  >> [add] ./lib/.env"
  cat ./setup/github.env > ./lib/.env
else
  echo "  >> [exists] ./lib/.env"
fi

# check if ./app/.env exists
if [ ! -f ./app/.env ] ; then
  echo "  >> [add] ./app/.env"
  cat ./setup/docker.env > ./app/.env
  echo >> ./app/.env
  cat ./setup/github.env >> ./app/.env
else
  echo "  >> [exists] ./app/.env"
fi
