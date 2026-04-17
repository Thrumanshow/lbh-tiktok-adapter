#!/usr/bin/env python3
# ================================================================
# 🐜 HORMIGASAIS · BOT DE CONTROL A16 CLEAN CORE
# Nodo: A16-SanMiguel-SV | Telegram Bridge ESTABLE
# ================================================================

import requests
import time
import os
import subprocess

# ── CONFIGURACIÓN FIJA (SIN RUIDO) ──────────────────────────────
BOT_TOKEN = "8414322465:AAFgwr4n4vN36rK3knCt3inJNzy-1xrVwU"
CHAT_ID = "8463843180"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── TELEMETRÍA LIMPIA ───────────────────────────────────────────
def send_lbh(msg):
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": f"🐜 A16:\n{msg}"
            },
            timeout=10
        )
    except Exception as e:
        print("error telegram:", e)

def get_updates(offset=None):
    try:
        params = {"timeout": 10}
        if offset:
            params["offset"] = offset

        r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=15)
        return r.json().get("result", [])
    except:
        return []

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout[:3000] if r.stdout else r.stderr[:3000]
    except Exception as e:
        return str(e)

# ── INICIO LIMPIO ───────────────────────────────────────────────
print("A16 CLEAN CORE activo")
send_lbh("✔ Telegram bridge estable (sin control_center)")

offset = None

# ── LOOP ÚNICO (SIN DOBLES SISTEMAS) ────────────────────────────
while True:
    updates = get_updates(offset)

    for u in updates:
        offset = u["update_id"] + 1

        if "message" not in u:
            continue

        text = u["message"].get("text", "")
        chat = str(u["message"]["chat"]["id"])

        if chat != CHAT_ID:
            continue

        print("CMD:", text)

        # ── COMANDOS LIMPIOS ───────────────────────────────

        if text == "/start":
            send_lbh(
                "/estado\n/reyna\n/cmd <comando>"
            )

        elif text == "/estado":
            send_lbh("A16 OK\nAPI OK\nGateway externo ignorado")

        elif text == "/reyna":
            send_lbh("activando misión...")
            subprocess.Popen(["bash", os.path.expanduser("~/lbh_control_center.sh")])

        elif text.startswith("/cmd "):
            cmd = text.replace("/cmd ", "")
            send_lbh(run(cmd))

        else:
            send_lbh("comando no reconocido")

    time.sleep(1)

