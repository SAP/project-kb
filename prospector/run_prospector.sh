#!/bin/bash

IMAGE_NAME="prospector-cli"

# check if base image and containers are spawned up
if [[ "$(docker images -q prospector-base:1.0 2> /dev/null)" == "" && "$(docker-compose ps -q backend db)" == "" ]]; then
    docker build -t prospector-base:1.0 -f docker/Dockerfile .
    docker-compose up -d --build
fi

# check if image is already built
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    # build the docker image
    docker build -t $IMAGE_NAME -f docker/cli/Dockerfile .
fi

# Function to extract the value of a specific option
get_option_value() {
  while [[ $# -gt 0 ]]; do
    if [[ $1 == "--report-filename" ]]; then
      echo "$2"
      return
    fi
    shift
  done
}

REPORT_FILENAME=$(get_option_value "$@")
if [[ -z $REPORT_FILENAME ]]; then
  OUTPUT_DIR="."
else
  OUTPUT_DIR=$(dirname "$REPORT_FILENAME")
fi

# run the docker container
docker run --network=prospector_default --rm -t -v $(pwd)/$OUTPUT_DIR:/app/results $IMAGE_NAME "$@"
