# TP1 — Distributed Data avec Docker

Mini-cluster pédagogique pour le TP 1 du cours **Données distribuées — M2 Big Data & IA**.

## Architecture

- 1 Leader
- 2 Followers
- 1 réseau Docker `distributed-net`
- API HTTP préparée à l'avance
- réplication simulée par envoi de la même donnée aux trois nœuds

```text
Client
  |
  v
Leader :8080
  |\
  | \
  v  v
F1:8081  F2:8082
     \  /
      \/
distributed-net
```

## Prérequis

- Git
- Docker Desktop
- Docker Compose
- Git Bash sous Windows (recommandé) ou terminal Linux/macOS
- `curl`

**Pas de Kubernetes / Minikube dans ce TP.**

## Démarrage rapide

```bash
docker compose build
docker compose up -d
docker ps
```

Tester :

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

Envoyer une donnée répliquée :

```bash
./scripts/send-data.sh product-001 "Produit A"
```

Vérifier :

```bash
curl http://localhost:8080/data
curl http://localhost:8081/data
curl http://localhost:8082/data
```

## Panne

```bash
docker stop node-follower-1
docker ps
```

## Partition réseau

```bash
docker network disconnect distributed-net node-follower-2
docker network inspect distributed-net
```

Reconnecter :

```bash
docker network connect distributed-net node-follower-2
```

## Nettoyage

```bash
docker compose down
```

## Organisation

```text
.
├── app/
│   ├── Dockerfile
│   └── app.py
├── docs/
├── scripts/
│   ├── cleanup.ps1
│   ├── cleanup.sh
│   ├── send-data.ps1
│   ├── send-data.sh
│   ├── start.ps1
│   ├── start.sh
│   ├── status.ps1
│   └── status.sh
├── student/
│   └── TP.md
├── docker-compose.yml
├── README.md
└── TP1.md
```

## Important

Ce projet est une **simulation pédagogique**. Les rôles Leader/Follower et la réplication ne constituent pas l'implémentation d'une base de données distribuée réelle.

Le TP vise à faire comprendre les concepts de :

- nœud ;
- réseau ;
- réplication ;
- panne ;
- partition réseau ;
- résilience ;
- cohérence ;
- complexité des systèmes distribués.
