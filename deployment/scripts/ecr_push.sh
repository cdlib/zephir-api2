#!/usr/bin/env bash

set -euo pipefail

ENVIRONMENT=$1

REPO_ROOT="$(dirname "$0")/../.."
DEPLOYMENT_ROOT="$REPO_ROOT/deployment"

# Quietly launch ECR if it doesn't exist
sceptre launch -y $ENVIRONMENT/ecr.yaml > /dev/null 2>&1

eval $(sceptre --ignore-dependencies list outputs $ENVIRONMENT/ecr.yaml --export=envvar)
ECR_URI="$SCEPTRE_RepositoryURI"

SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"

LOCAL_IMAGE="zephir-api-local"
SHA_IMAGE="$ECR_URI:$SHA"
LATEST_IMAGE="$ECR_URI:latest"

echo "===== STARTING ECR PUSH ====="

echo "===== Logging in to AWS ECR ====="
ECR_REGISTRY=$(echo "$ECR_URI" | cut -d'/' -f1)
aws ecr get-login-password --region "${AWS_REGION:-us-west-2}" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

echo "===== Building Dockerfile ====="
export DOCKER_DEFAULT_PLATFORM=linux/amd64 # For Docker to build on M-series Macs, comment out if not applicable.
docker build --no-cache --tag "$LOCAL_IMAGE" --target production "$REPO_ROOT"

echo "===== Tagging Docker Image ====="
docker tag "$LOCAL_IMAGE" "$SHA_IMAGE"
docker tag "$LOCAL_IMAGE" "$LATEST_IMAGE"

echo "===== Pushing image to ECR ====="
docker push "$SHA_IMAGE"
docker push "$LATEST_IMAGE"

echo "===== ECR PUSH COMPLETE ====="
