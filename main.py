import os
import time
import requests
from telegram import Bot

# === CONFIG ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ADDRESSES = [
    "bc1qmnjn0l0kdf3m3d8khc6cukj8deak8z24g",
    "bc1qg7dy3upmf0qdsf52y27gzvh2zh6zwqg5w9u7n6",
    "bc1q2ehxfguefcak9lvu35xmqwwll7q8cftq6cd5fc",
    "bc1q62l42z0x6eqwyf5ygp9gnjvdf2pw0dgyk32cwg",
    "bc1q4vwuhx5wnqswmvmt9fvkywgt35gf8jgmf5qfdc",
    "bc1q3um4f9eyxey8ue26nldm97qh9pk3fvkr76e80g",
    "bc1q8lvkr7wklv2t5sg9a5qpevmvh6ur4x74ylgnmn",
    "bc1qvzk67qcdmj3c3tw7tg9hq6m3a6xfgs7k7rhjdy"
]

CHECK_INTERVAL = 60  # secondes

bot = Bot(token=TELEGRAM_TOKEN)

seen_txids = {addr: set() for addr in ADDRESSES}

def get_transactions(address):
    try:
        url = f"https://blockstream.info/api/address/{address}/txs"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[API ERROR] {address} : {e}")
        return []

def notify(tx, address):
    txid = tx["txid"]
    link = f"https://blockstream.info/tx/{txid}"
    msg = f"🚨 Sortie BTC détectée !\nAdresse : `{address}`\nTxID : `{txid}`\n🔗 {link}"
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")
        print(f"[ALERTE] Envoyée : {txid}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

def check_address(address):
    txs = get_transactions(address)
    for tx in txs:
        txid = tx["txid"]
        if txid in seen_txids[address]:
            continue
        seen_txids[address].add(txid)

        for vin in tx.get("vin", []):
            if vin.get("prevout", {}).get("scriptpubkey_address") == address:
                notify(tx, address)
                break

def main():
    print("🟢 Surveillance BTC active sur Railway")
    while True:
        for address in ADDRESSES:
            check_address(address)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
