#!/usr/bin/env bash

ENVIRONMENT=$1
IMAGE_TAG=${2:-""}

# Assumes there is at least one image in ECR
if [[ -n "$IMAGE_TAG" ]]; then
    uv run sceptre --var image_tag="$IMAGE_TAG" launch -y $ENVIRONMENT
else
    uv run sceptre launch -y $ENVIRONMENT
fi
