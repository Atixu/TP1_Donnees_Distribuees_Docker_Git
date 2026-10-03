# Notes enseignant — TP1

## Intention pédagogique

Ce TP doit précéder Kubernetes. Il sert à faire émerger les problèmes du distribué avant d'introduire l'orchestration.

## Points à faire ressortir

1. Plusieurs conteneurs ne constituent pas automatiquement un système distribué robuste.
2. La communication réseau est une dépendance.
3. La réplication améliore la redondance mais crée des problèmes de cohérence.
4. Un nœud peut être vivant mais isolé du réseau.
5. Distribuer ne signifie pas seulement "ajouter des machines".
6. La suite du cours introduira partitionnement, cohérence, consensus et bases distribuées.

## Démonstration rapide

```bash
docker compose build
docker compose up -d
docker ps

curl http://localhost:8080/health
./scripts/send-data.sh demo-001 "Test"

docker stop node-follower-1
curl http://localhost:8080/health

docker start node-follower-1
docker network disconnect distributed-net node-follower-2
docker network inspect distributed-net
docker network connect distributed-net node-follower-2
```

## Attention

La réplication du TP est volontairement simulée par `scripts/send-data.sh`. Ne pas la présenter comme une réplication transactionnelle ou consensus d'une base distribuée réelle.

## API des étudiants

Les groupes peuvent utiliser une API publique de leur choix et développer uniquement le client nécessaire à l'extraction et à l'envoi des données.
