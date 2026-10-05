import json
import urllib.request
from datetime import datetime, timezone

CRYPTOS = {
    "Bitcoin":   "bitcoin",
    "Ethereum":  "ethereum",
    "Solana":    "solana",
    "XRP":       "ripple",
    "Cardano":   "cardano",
    "Dogecoin":  "dogecoin",
    "Litecoin":  "litecoin",
    "Polkadot":  "polkadot",
}

LEADER = "http://localhost:8080"

ids = ",".join(CRYPTOS.values())

url = (f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
       f"&vs_currencies=eur"
       f"&include_market_cap=true&include_24hr_change=true&include_last_updated_at=true")

req = urllib.request.Request(url, headers={"User-Agent": "tp-donnees-distribuees"})
cours = json.load(urllib.request.urlopen(req, timeout=15))

for nom, cg_id in CRYPTOS.items():
    c = cours[cg_id]
    payload = {
        "key": nom,
        "value": {
            "prix_eur": c["eur"],
            "variation_24h_pct": round(c["eur_24h_change"], 2),
            "market_cap_eur": round(c["eur_market_cap"]),
            "maj": datetime.fromtimestamp(c["last_updated_at"], timezone.utc).strftime("%Y-%m-%dT%H:%M"),
        },
    }
    req = urllib.request.Request(
        f"{LEADER}/data",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    rep = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    print(f"{nom:10} {rep['message']}  {rep['replication']}")

print(f"\n{len(CRYPTOS)} cryptos injectees dans le leader.")
