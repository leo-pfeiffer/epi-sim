#!/bin/bash
set -eu pipefail

my_expected_name=./data_processing/generate_data_paths.sh
my_actual_name=$0

if [ "$my_expected_name" != "$my_actual_name" ]; then
  echo "Please run me from the project root" >&2
  exit 1
fi

if [ ! -d "./data_processing/data" ] ; then
  echo ">> [add] /data"
  mkdir ./data_processing/data
else
  echo ">> [exists] /data"
fi

if [ ! -d "./data_processing/data/raw" ] ; then
  echo ">> [add] /data/raw"
  mkdir ./data_processing/data/raw
else
  echo ">> [exists] /data/raw"
fi

if [ ! -d "./data_processing/data/out" ] ; then
  echo ">> [add] /data/out"
  mkdir ./data_processing/data/out
else
  echo ">> [exists] /data/out"
fi

if [ ! -d "./data_processing/data/graphics" ] ; then
  echo ">> [add] /data/graphics"
  mkdir ./data_processing/data/graphics
else
  echo ">> [exists] /data/graphics"
fi

if [ ! -d "./data_processing/data/graphs" ] ; then
  echo ">> [add] /data/graphs"
  mkdir ./data_processing/data/graphs
else
  echo ">> [exists] /data/graphs"
fi
