#!/usr/bin/env bash

cd "$(dirname "$0")/.."  # run from deployment/ so sceptre resolves config/ and templates/

ENVIRONMENT=$1

uv run sceptre delete -y $ENVIRONMENT/ecs.yaml
