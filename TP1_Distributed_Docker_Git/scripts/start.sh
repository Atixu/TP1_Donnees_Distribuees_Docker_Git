#!/usr/bin/env bash
set -e
docker compose build
docker compose up -d
echo
echo "Cluster démarré."
docker ps --filter "name=node-"
