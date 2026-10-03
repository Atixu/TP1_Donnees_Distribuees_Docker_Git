#!/usr/bin/env bash
docker compose down
docker network rm distributed-net 2>/dev/null || true
