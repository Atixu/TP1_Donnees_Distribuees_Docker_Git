#!/usr/bin/env bash
echo "=== Conteneurs ==="
docker ps --filter "name=node-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo
echo "=== Réseau ==="
docker network inspect distributed-net --format '{{range .Containers}}{{.Name}} -> {{.IPv4Address}}{{"\n"}}{{end}}'
