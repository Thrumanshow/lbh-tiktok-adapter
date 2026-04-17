#!/usr/bin/env python3

import requests, time, os, re, sys
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

BOT_TOKEN = "8414322465:AAFgwr4ny4vN36rK3knCt3inJNzy-1xrVwU"
CHAT_ID   = "8463843180"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ================================================================
# IMPORTAR TRANSMUTADOR
# ================================================================

sys.path.append(os.path.expanduser("~/lbh-tiktok-adapter/src"))

from lbh_transmutador_url import (
    extraer_video_id,
    metricas_to_feromonas,
    inyectar_en_colonia
)

# ================================================================
# UTILS
# ================================================================

def send(msg):
    try:
        requests.post(f"{BASE_URL}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg[:4000]
        })
    except:
        print("[ERROR] envio telegram")

def get_updates(offset=None):
    params = {"timeout": 5}
    if offset:
        params["offset"] = offset

    try:
        res = requests.get(f"{BASE_URL}/getUpdates", params=params)
        return res.json().get("result", [])
    except:
        return []

# ================================================================
# TRANSMUTADOR
# ================================================================

def procesar_lbh(url):
    video_id = extraer_video_id(url)

    metricas = {
        "views": 0,
        "likes": 0,
        "comments": 0,
        "saves": 0,
        "shares": 0,
        "purchases": 0
    }

    mision, paquetes, score = metricas_to_feromonas(video_id, metricas)
    inyectar_en_colonia(video_id, mision, paquetes)

    # reporte
    msg = f"🐜 LBH TRANSMUTACIÓN\n\n"
    msg += f"🎯 Video: {video_id}\n"
    msg += f"🔥 Score: {score}/999\n\n"

    for p in paquetes[:5]:
        msg += f"• {p['campo']}: {p['valor']} → {p['objetivo']}\n"

    msg += "\n🧬 ADN generado y enviado al enjambre"

    return msg

# ================================================================
# BOT LOOP
# ================================================================

print("🐜 HormigasAIS · Telegram LBH activo...")

offset = None

while True:
    updates = get_updates(offset)

    for u in updates:
        offset = u["update_id"] + 1

        if "message" not in u:
            continue

        text = u["message"].get("text", "")
        print("📩", text)

        # ─────────────────────────────
        # AUTO DETECCIÓN (sin comando)
        # ─────────────────────────────
        urls = re.findall(r"https://vt\.tiktok\.com/[A-Za-z0-9]+", text)

        if urls:
            for url in urls:
                send("⚙️ URL detectada automáticamente...")
                result = procesar_lbh(url)
                send(result)
            continue

        # ─────────────────────────────
        # COMANDOS
        # ─────────────────────────────

        if text == "/start":
            send("🐜 HormigasAIS conectado.\nComandos:\n/lbh URL\n/estado\n/cmd")

        elif text == "/estado":
            send("📡 Nodo A16 activo\n🧬 LBH operativo\n🔥 Enjambre vivo")

        elif text.startswith("/lbh"):
            try:
                url = text.split(" ")[1]

                if "tiktok.com" not in url:
                    send("❌ URL inválida")
                    continue

                send("⚙️ Procesando LBH...")
                result = procesar_lbh(url)
                send(result)

            except:
                send("❌ Uso: /lbh https://vt.tiktok.com/...")

        elif text.startswith("/cmd"):
            cmd = text.replace("/cmd ", "")
            output = os.popen(cmd).read()
            send(f"💻 Resultado:\n{output[:4000]}")

        else:
            send("❓ Comando no reconocido")

    time.sleep(2)

