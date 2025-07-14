import requests
import time
import os

# Variables d’environnement
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Liste des adresses BTC à surveiller (corrigées)
ADDRESSES = [
    "bc1qmnjn0l0kdf3m3d8khc6cukj8deakg8m588z24g",
    "bc1qymu2qf0d23qg38p9w7yxxt4yqjjg47rytxujl6",
    "bc1qnzy2rr7g3688x62f8vrhgeclvtcs5hr50wzu0w",
    "bc1q2lkyqvqqwus9pl96krgtk4rh0fqu8gtmpuwgmc",
    "bc1qhtawge4km6juhlkrnvt7qjahhsc96qdlgf3c8t",
    "bc1q84w6epn6uce9s85slt7q6emm3qfzz7ngq7ef6k",
    "bc1qwq5geath93h0lnfsrmnwnfuck2f9ypv4ewyl4j",
    "1GcCK347TMbzHrRpDoVvJdR6eyECyqHCiU"
    "bc1qmuxrzvnx34j8y6h9leg4zen5gnw7wmfmgp8v2p"
    "bc1qrn8pjas098hfn42d578v6vxg4nh6kn4dvdeevy"
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
                print(f"Contenu brut (100 premiers caractères) : {res.text[:100]}")
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
    send_telegram_alert("🎯 Surveillance des adresses BTC lancée.")
    while True:
        check_transactions()
        time.sleep(60)
