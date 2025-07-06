import requests
import time
import os

# Variables d’environnement
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 8 adresses BTC à surveiller
ADDRESSES = [
    "bc1qmnjn0l0kdf3m3d8khc6cukj8deak8z24g",
    "bc1qylg06gsplwqgtxcr7f45klzcp9jk6v63enpn7j",
    "bc1qqaqnhs4kcdgkztsvm3ry7ph8t9c2ysqjmuymqj",
    "bc1q9kfvq7dxyl3vd0hz4st9xmd26ydcxtcwklc3qv",
    "bc1qyyq67q3lwsrm2j5tpw2mvzujctgh0wq3p4ad0r",
    "bc1qth08spwknh3gw0upzuywtky7ly9ef4z6pjzlh6",
    "bc1q0pghnphf7vqyz7pkaz7qkysccrflg9zz8t70yx",
    "bc1q9x2rt34y37y2gkycux4hnmfywm7t3cv6vw4tdf"
]

seen_txids = set()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, json=payload)
        print(f"Télégram → {r.status_code}")
    except Exception as e:
        print(f"Erreur Telegram : {e}")

def check_transactions():
    for address in ADDRESSES:
        try:
            url = f"https://mempool.space/api/address/{address}/txs"
            res = requests.get(url, timeout=10)

            print(f"→ {address} : {res.status_code}")

            if res.status_code != 200:
                print(f"Contenu : {res.text}")  # Affiche le contenu brut pour l'erreur
                continue

            txs = res.json()

            if not txs:
                print(f"Aucune transaction trouvée pour {address}.")
                continue

            for tx in txs:
                txid = tx["txid"]
                if txid in seen_txids:
                    continue

                for vin in tx.get("vin", []):
                    if "prevout" in vin and vin["prevout"].get("scriptpubkey_address") == address:
                        msg = f"📤 Sortie BTC détectée depuis {address}\n🔗 https://mempool.space/tx/{txid}"
                        send_telegram_alert(msg)
                        break

                seen_txids.add(txid)

        except Exception as e:
            print(f"Erreur pour {address} : {e}")

if __name__ == "__main__":
    print("🎯 Démarrage de la surveillance...")
    while True:
        check_transactions()
        time.sleep(60)  # Vérifie toutes les 60 secondes
