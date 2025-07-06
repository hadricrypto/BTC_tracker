import time
import requests
import os
from telegram import Bot

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # ou remplace par ton token en dur
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # ou remplace par ton chat_id
BTC_ADDRESS = "bc1qmnjn0l0kdf3m3d8khc6cukj8deak8z24g"
CHECK_INTERVAL = 60  # en secondes

bot = Bot(token=TELEGRAM_TOKEN)

# === UTILITAIRE ===
def get_latest_txids(address):
    url = f"https://blockstream.info/api/address/{address}/txs/chain"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        txs = response.json()
        return [tx["txid"] for tx in txs]
    except Exception as e:
        print(f"[ERREUR API] {e}")
        return None

# === BOUCLE PRINCIPALE ===
def main():
    print("🎯 Lancement de la surveillance de l’adresse BTC...")
    last_seen_txids = get_latest_txids(BTC_ADDRESS)
    if last_seen_txids is None:
        print("❌ Impossible d'obtenir les transactions initiales.")
        return

    while True:
        time.sleep(CHECK_INTERVAL)
        current_txids = get_latest_txids(BTC_ADDRESS)
        if current_txids is None:
            print("⚠️ Erreur API temporaire, on réessaie au prochain tour.")
            continue

        new_txids = [txid for txid in current_txids if txid not in last_seen_txids]
        if new_txids:
            for txid in new_txids:
                message = f"💰 Nouvelle transaction détectée sur l’adresse BTC :\nhttps://blockstream.info/tx/{txid}"
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                print(f"[✔️] Notification envoyée pour la transaction {txid}")
            last_seen_txids = current_txids
        else:
            print("🔍 Aucune nouvelle transaction détectée.")

if __name__ == "__main__":
    main()
