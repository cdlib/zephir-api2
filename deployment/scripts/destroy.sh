#!/usr/bin/env bash

ENVIRONMENT=$1

uv run sceptre delete -y $ENVIRONMENT/ecs.yaml
