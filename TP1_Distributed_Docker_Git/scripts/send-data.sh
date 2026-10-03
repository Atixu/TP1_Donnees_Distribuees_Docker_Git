#!/usr/bin/env bash
set -e

KEY="${1:-product-001}"
VALUE="${2:-Produit A}"

echo "==> Envoi vers le Leader"
curl -s -X POST http://localhost:8080/data \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\",\"value\":\"${VALUE}\"}"
echo

echo "==> Simulation de réplication vers Follower 1"
curl -s -X POST http://localhost:8081/data \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\",\"value\":\"${VALUE}\"}"
echo

echo "==> Simulation de réplication vers Follower 2"
curl -s -X POST http://localhost:8082/data \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\",\"value\":\"${VALUE}\"}"
echo

echo
echo "==> Vérification"
curl -s http://localhost:8080/data; echo
curl -s http://localhost:8081/data; echo
curl -s http://localhost:8082/data; echo
