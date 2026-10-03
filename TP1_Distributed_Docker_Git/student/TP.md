# TP 1 — Guide étudiant

Le TP complet à suivre est fourni dans le document `TP1.md` à la racine du projet.

## Démarrage rapide

### 1. Vérifier l'environnement

```bash
git --version
docker --version
docker compose version
```

### 2. Démarrer le cluster

Sous Git Bash :

```bash
./scripts/start.sh
```

Ou directement :

```bash
docker compose build
docker compose up -d
```

### 3. Vérifier

```bash
docker ps
```

### 4. Tester

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### 5. Envoyer une donnée

```bash
./scripts/send-data.sh product-001 "Produit A"
```

Puis :

```bash
curl http://localhost:8080/data
curl http://localhost:8081/data
curl http://localhost:8082/data
```

Les trois nœuds contiennent la donnée dans cette simulation.

## Important

L'application fournie est volontairement simple. La réplication est **simulée** par l'envoi de la même donnée aux trois nœuds. Le TP porte sur les concepts d'architecture distribuée, pas sur l'implémentation d'un moteur de réplication industriel.

Consultez `TP1.md` pour les étapes, questions, mini-projet API et livrables.
