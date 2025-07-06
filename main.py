import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            print(f"Erreur Telegram: {response.text}")
    except Exception as e:
        print(f"Erreur lors de l'envoi Telegram : {e}")

def check_transactions():
    for address in ADDRESSES:
        try:
            url = f"https://blockstream.info/api/address/{address}/txs"
            res = requests.get(url, timeout=10)
            txs = res.json()

            for tx in txs:
                txid = tx["txid"]
                if txid in seen_txids:
                    continue

                for vin in tx.get("vin", []):
                    if "prevout" in vin and vin["prevout"].get("scriptpubkey_address") == address:
                        msg = f"📤 Sortie BTC détectée depuis {address}\n🔗 TX : https://blockstream.info/tx/{txid}"
                        send_telegram_alert(msg)
                        break

                seen_txids.add(txid)

        except Exception as e:
            print(f"Erreur pour {address} : {e}")

if __name__ == "__main__":
    while True:
        check_transactions()
        time.sleep(60)
