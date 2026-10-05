# Mini-projet données distribuées : réplication de cours crypto

API choisie : **CoinGecko** (`/api/v3/simple/price`). Elle est publique et ne demande pas de clé. Elle donne en temps réel le prix en euros, la variation sur 24 h et la capitalisation de 8 cryptomonnaies.

Le cluster est celui du TP « Réplication » ([TP1-Seance2-Replication](https://github.com/Santoudllo/TP1-Seance2-Replication)) : 3 nœuds Flask (`replication-node-1/2/3` sur les ports 8080/8081/8082), qui répliquent chaque écriture vers leurs pairs et se resynchronisent toutes les 2 s.

## 1. Créer le réseau

```bash
docker network create --driver bridge distributed-net
docker network ls
# docker network rm <id du réseau>   (pour le supprimer)
```

## 2. Démarrer le cluster

Dans le dossier `TP1-Seance2-Replication` :

```bash
docker compose build
docker compose up -d
docker ps
```

## 3. Tester les nœuds

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

```json
{"data_count":0,"node":"node-1","status":"UP"}
{"data_count":0,"node":"node-2","status":"UP"}
{"data_count":0,"node":"node-3","status":"UP"}
```

## 4. État initial

```bash
curl http://localhost:8080/data   # idem 8081, 8082
```

```json
{"count":0,"data":{},"node":"node-1"}
{"count":0,"data":{},"node":"node-2"}
{"count":0,"data":{},"node":"node-3"}
```

## 5. Injecter les données de l'API

Le script [inject-crypto.py](inject-crypto.py) appelle CoinGecko une seule fois pour les 8 cryptos. Il envoie ensuite chaque crypto au nœud 1 (`POST /data`), qui la réplique vers les nœuds 2 et 3.

```bash
python3 inject-crypto.py      # Windows : py inject-crypto.py
```

> Sur macOS, si Python a été installé depuis python.org et renvoie `CERTIFICATE_VERIFY_FAILED`, lancer `SSL_CERT_FILE=/etc/ssl/cert.pem python3 inject-crypto.py`, ou exécuter une fois `Install Certificates.command`.

```text
Bitcoin    data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Ethereum   data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Solana     data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
XRP        data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Cardano    data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Dogecoin   data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Litecoin   data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}
Polkadot   data stored and replicated  {'http://replication-node-2:8080': 'OK', 'http://replication-node-3:8080': 'OK'}

8 cryptos injectees dans le leader.
```

État des nœuds : `count: 8` sur les trois. Extrait de `http://localhost:8081/data` :

```json
{
  "count": 8,
  "data": {
    "Bitcoin": {
      "maj": "2026-10-05T14:43",
      "market_cap_eur": 1539184516325,
      "prix_eur": 76622,
      "variation_24h_pct": 1.37
    },
    "Cardano": {
      "maj": "2026-10-05T14:43",
      "market_cap_eur": 9066696310,
      "prix_eur": 0.241475,
      "variation_24h_pct": 10.74
    },
    ...
  },
  "node": "node-2"
}
```

## 6. Arrêter le nœud 2

```bash
docker stop replication-node-2
```

## 7. Ajouter une donnée pendant la panne

```bash
curl -X POST http://localhost:8080/data -H "Content-Type: application/json" \
  -d '{"key":"Avalanche","value":{"prix_eur":21.35,"variation_24h_pct":2.1,"market_cap_eur":8900000000,"maj":"2026-10-05T14:45"}}'
```

Sous PowerShell :

```powershell
curl.exe -s -X POST http://localhost:8080/data -H "Content-Type: application/json" -d '{\"key\":\"Avalanche\",\"value\":{\"prix_eur\":21.35,\"variation_24h_pct\":2.1,\"market_cap_eur\":8900000000,\"maj\":\"2026-10-05T14:45\"}}'
```

Réponse :

```json
{"message":"data stored and replicated","node":"node-1",
 "replication":{"http://replication-node-2:8080":"UNAVAILABLE: URLError",
                "http://replication-node-3:8080":"OK"}}
```

État des nœuds :

```text
node-1 : 9 cryptos (avec Avalanche)
node-2 : injoignable (port 8081)
node-3 : 9 cryptos (avec Avalanche)
```

Le service reste disponible en lecture et en écriture. Seul le nœud arrêté manque l'écriture.

## 8. Redémarrer le nœud 2

```bash
docker start replication-node-2
```

État des nœuds après quelques secondes :

```text
node-1 : 9 cryptos
node-2 : 9 cryptos (avec Avalanche)
node-3 : 9 cryptos
```

Les données ne sont gardées qu'en mémoire, donc le nœud 2 redémarre **vide**. Son thread de synchronisation interroge un pair toutes les 2 s (`GET /internal/data`) et récupère tout son état. Il obtient ainsi **Avalanche**, la donnée écrite pendant son absence, sans aucune intervention.

## Questions

### Quel est le rôle de chaque nœud dans l'architecture ?

| Nœud | Conteneur | Port hôte | Rôle |
|---|---|---|---|
| Leader | `replication-node-1` | 8080 | Reçoit les écritures du client (`inject-crypto.py`, `curl`). Il stocke chaque crypto puis la **propage** aux deux autres nœuds (`POST /internal/replicate`). |
| Follower 1 | `replication-node-2` | 8081 | Garde une **copie** des données. C'est le nœud qu'on arrête : en revenant, il se resynchronise auprès d'un pair (`GET /internal/data`). |
| Follower 2 | `replication-node-3` | 8082 | Garde une autre **copie**. Pendant la panne du follower 1, il continue de recevoir les écritures, donc il reste au moins 2 copies à jour. |

Dans ce code, les trois nœuds exécutent la même application. Le nœud 1 n'est « Leader » que parce que le client lui envoie toutes les écritures. Une écriture envoyée sur 8081 ou 8082 serait elle aussi répliquée. Chaque nœud peut répondre aux lectures (`GET /data`), ce qui assure la disponibilité si un nœud tombe.

### Comment Docker permet-il au Leader de retrouver node-follower-1 ?

Grâce au **DNS interne de Docker**. Les conteneurs sont tous reliés au même réseau bridge défini par l'utilisateur (`distributed-net`). Sur ce type de réseau, Docker fournit un serveur DNS (`127.0.0.11`) qui associe chaque **nom de conteneur ou de service** à son adresse IP sur le réseau :

```text
$ docker exec replication-node-1 cat /etc/resolv.conf
nameserver 127.0.0.11

$ docker exec replication-node-1 python -c "import socket; print(socket.gethostbyname('replication-node-2'))"
172.21.0.2
```

Le Leader connaît donc ses pairs par leur nom, avec la variable `PEERS=http://replication-node-2:8080,http://replication-node-3:8080` du `docker-compose.yml`, et jamais par leur IP. C'est important parce que l'IP peut changer quand le conteneur est recréé (`docker rm -f` puis `docker compose up`), alors que le nom reste le même. Le réseau par défaut `bridge` n'offre pas cette résolution par nom, d'où la création préalable de `distributed-net`.

Avec le nom de l'architecture Leader/Follower du TP1, le principe est le même : le Leader joint `http://node-follower-1:8080`, et Docker traduit `node-follower-1` en IP.

### Pourquoi la communication réseau devient-elle importante dans une architecture distribuée ?

Les nœuds ne partagent ni mémoire ni disque. **Le réseau est leur seul moyen d'échanger des données**. Toutes les fonctions du projet en dépendent :

- **Réplication** : une écriture n'existe sur les followers que si l'appel HTTP du Leader aboutit.
- **Détection de panne** : le Leader ne « sait » qu'un nœud est tombé que parce que l'appel réseau échoue (`UNAVAILABLE: URLError`).
- **Resynchronisation** : le follower revenu récupère son retard en interrogeant un pair sur le réseau.
- **Cohérence** : tant qu'un message n'est pas arrivé, les copies divergent. Le follower 1 n'avait pas Avalanche pendant sa panne.

Le réseau introduit aussi des problèmes qui n'existent pas sur une seule machine : **latence**, **messages perdus**, **timeouts** (ici 1,5 s par pair), nœuds injoignables, partitions réseau. Une architecture distribuée doit être conçue en sachant que le réseau peut tomber en panne. C'est l'hypothèse de départ du théorème CAP.

### Quelle différence avec une application utilisant uniquement localhost ?

`localhost` (127.0.0.1) désigne **la machine ou le conteneur lui-même**. Dans Docker, chaque conteneur a son propre espace réseau, donc son propre `localhost`. Depuis le Leader, `localhost:8081` ne mène pas au follower 1 :

```text
$ docker exec replication-node-1 python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')"
urllib.error.URLError: <urlopen error [Errno 111] Connection refused>
```

| Application en localhost | Application distribuée (ce projet) |
|---|---|
| Un seul processus ou une seule machine, les composants se parlent localement | Plusieurs nœuds isolés qui se parlent à travers un réseau |
| Adresse fixe `127.0.0.1` | Noms de service résolus par DNS (`replication-node-2`) |
| Si la machine tombe, tout s'arrête (point de défaillance unique) | Si un nœud tombe, les autres continuent de servir |
| Une seule copie des données | Plusieurs copies répliquées |
| Pas de latence ni de perte réseau à gérer | Il faut gérer les timeouts, les pannes et la cohérence entre les copies |
| Montée en charge limitée à une machine | Montée en charge possible en ajoutant des nœuds |

`localhost` reste utilisé dans ce projet, mais uniquement **depuis la machine hôte** : `localhost:8080/8081/8082` passe par les ports publiés par Docker (`ports:` dans le compose). Entre eux, les nœuds communiquent uniquement par leur nom sur `distributed-net`.

## Conclusion

- **Réplication** : chaque cours injecté existe en 3 copies, une par nœud.
- **Disponibilité** : quand un nœud tombe, le cluster continue d'accepter les écritures sur les réplicas restants.
- **Resynchronisation** : le nœud qui revient rattrape automatiquement son retard à partir d'un pair disponible.
- **Limites** : les données sont uniquement en mémoire, rien ne versionne les écritures (si deux nœuds reçoivent des valeurs différentes pour la même clé, aucune règle ne décide laquelle garder) et il n'y a pas de quorum. Avec des données qui changent vite, comme des cours de crypto, un réplica en retard renverrait un prix **périmé**. C'est exactement le problème de cohérence que traitent les vrais SGBD distribués comme Cassandra.
