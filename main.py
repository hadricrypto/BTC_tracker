import requests
import time
import os

from telegram import Bot

# Clé du bot Telegram et chat ID (via variables Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

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

# Historique pour éviter les doublons
already_seen = set()

def check_transactions():
    for address in ADDRESSES:
        url = f"https://blockstream.info/api/address/{address}/txs"
        try:
            response = requests.get(url, timeout=10)
            txs = response.json()
            for tx in txs:
                txid = tx["txid"]
                if txid in already_seen:
                    continue
                # Vérifie que l’adresse apparaît dans les entrées (sortie BTC)
                for vin in tx.get("vin", []):
                    if "prevout" in vin:
                        addr = vin["prevout"].get("scriptpubkey_address", "")
                        if addr == address:
                            message = f"📤 Sortie BTC détectée depuis {address}\nTX: https://blockstream.info/tx/{txid}"
                            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                            print(f"Alerte envoyée pour {txid}")
                            break
                already_seen.add(txid)
        except Exception as e:
            print(f"Erreur pour {address} : {e}")

if __name__ == "__main__":
    while True:
        check_transactions()
        time.sleep(60)  # Vérifie toutes les minutes
