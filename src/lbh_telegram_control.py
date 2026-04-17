#!/usr/bin/env python3
import os, time, json, sqlite3, socket, requests, subprocess
from threading import Thread

# CONFIGURACIÓN SOBERANA
NODE_ID   = socket.gethostname()
BOT_TOKEN = "8414322465:AAFgwr4ny4vN36rK3knCt3inJNzy-1xrVwU"
CHAT_ID   = "8463843180"
BASE_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}"
DB        = os.path.expanduser("~/reyna_v11.db")
REPORTE   = os.path.expanduser("~/hormigasais-lab/logs/REPORTE_MISION.md")
user_states = {}

def send(msg):
    try:
        requests.post(f"{BASE_URL}/sendMessage", 
                     data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, 
                     timeout=10)
    except: pass

def handle(chat_id, text):
    global user_states
    raw_text = text.strip()

    # PRIORIDAD SOBERANA H9
    if raw_text.startswith("/h9"):
        user_states.pop(chat_id, None)
        try:
            url = raw_text.split(" ")[1]
            h9_path = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h9_orquestador.py")
            subprocess.Popen(["python3", h9_path, url])
            send(f"🧬 *[H9-AUTÓNOMO]*\nNodo A16 activado.\n🔗 URL: {url}")
            return
        except Exception as e:
            send(f"⚠️ Error H9: {str(e)}")
            return

    # Lógica de comandos estándar
    cmd = raw_text.lower()
    if cmd == "/start":
        send("👑 REYNA v12.4 ONLINE\nNodo A16 listo.")
    elif cmd == "/reporte":
        send("Enviando reporte soberano...")
        # Aquí iría tu lógica de send_report()

def listener():
    offset = None
    while True:
        try:
            r = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 30}).json()
            if r.get("result"):
                for u in r["result"]:
                    offset = u["update_id"] + 1
                    if "message" in u and "text" in u["message"]:
                        handle(str(u["message"]["chat"]["id"]), u["message"]["text"])
        except: time.sleep(5)

if __name__ == "__main__":
    print("👑 REYNA v12.4 ONLINE (FIXED)")
    Thread(target=listener).start()
