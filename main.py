import time
import asyncio
import requests
from telegram import Bot

# === Configuration ===
WATCHED_ADDRESSES = {
    "bc1qmnjn0l0kdf3m3d8khc6cukj8deak8z24g",
    "bc1qymu2qf0d23qg38p9w7yxxt4yqjjg47rytxujl6",
    "bc1qnzy2rr7g3688x62f8vrhgeclvtcs5hr50wzu0w",
    "bc1q2lkyqvqqwus9pl96krgtk4rh0fqu8gtmpuwgmc",
    "bc1qhtawge4km6juhlkrnvt7qjahhsc96qdlgf3c8t",
    "bc1q84w6epn6uce9s85slt7q6emm3qfzz7ngq7ef6k",
    "bc1qwq5geath93h0lnfsrmnwnfuck2f9ypv4ewyl4j",
    "1GcCK347TMbzHrRpDoVvJdR6eyECyqHCiU"
}

BOT_TOKEN = "TON_BOT_TOKEN_TELEGRAM"
CHAT_ID = "TON_CHAT_ID_TELEGRAM"
CHECK_INTERVAL = 60  # en secondes

bot = Bot(token=BOT_TOKEN)
seen_txids = set()

async def send_alert(message: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"[ALERTE] {message}")
    except Exception as e:
        print(f"[ERREUR TELEGRAM] {e}")

async def check_transactions():
    for address in WATCHED_ADDRESSES:
        url = f"https://blockstream.info/api/address/{address}/txs"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[ERREUR API] {url}")
                continue

            txs = response.json()
            for tx in txs:
                txid = tx.get("txid")
                if txid in seen_txids:
                    continue
                seen_txids.add(txid)

                # Entrées (vin)
                for vin in tx.get("vin", []):
                    from_addr = vin.get("prevout", {}).get("scriptpubkey_address")
                    value = vin.get("prevout", {}).get("value", 0) / 1e8
                    if from_addr in WATCHED_ADDRESSES and value >= 1:
                        await send_alert(f"🔴 Départ de {value:.2f} BTC depuis {from_addr}\n➡️ https://mempool.space/tx/{txid}")

                # Sorties (vout)
                destinations = set()
                for vout in tx.get("vout", []):
                    script_type = vout.get("scriptpubkey_type")
                    to_addr = vout.get("scriptpubkey_address")
                    value = vout.get("value", 0) / 1e8

                    if script_type != "op_return" and to_addr:
                        destinations.add(to_addr)
                        if to_addr in WATCHED_ADDRESSES and value >= 1:
                            await send_alert(f"🟢 Arrivée de {value:.2f} BTC vers {to_addr}\n➡️ https://mempool.space/tx/{txid}")

                # OP_RETURN
                source_addresses = {
                    vin.get("prevout", {}).get("scriptpubkey_address")
                    for vin in tx.get("vin", [])
                }
                all_addresses = source_addresses.union(destinations)
                for vout in tx.get("vout", []):
                    if vout.get("scriptpubkey_type") == "op_return":
                        if WATCHED_ADDRESSES & all_addresses:
                            data_hex = vout.get("scriptpubkey", "")
                            await send_alert(f"📦 OP_RETURN détecté : {data_hex}\n➡️ https://mempool.space/tx/{txid}")

        except Exception as e:
            print(f"[ERREUR] {e}")

async def main_loop():
    while True:
        await check_transactions()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main_loop())
