#!/usr/bin/env python3

import sqlite3, os, time, hmac, hashlib, json, re, socket, requests
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

HMAC_KEY    = b"hormigasais-sovereign-2026"
NODE_ORIGIN = "A16-SanMiguel-SV"
UDP_PORT    = 5005

DB_COLONY   = os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db")

WATCH_FILE  = "/sdcard/Download/tiktok_links.txt"

TELEGRAM_TOKEN = "TU_TOKEN"
TELEGRAM_URL   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

# ================================================================
# CORE LBH
# ================================================================

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def extraer_video_id(url):
    m = re.search(r"vt\.tiktok\.com/([A-Za-z0-9]+)", url)
    return m.group(1) if m else url.split("/")[-1]

def metricas_to_feromonas(video_id, metricas):
    ts = int(time.time())
    score = sum(metricas.values()) % 999

    paquetes = []
    for campo, valor in metricas.items():
        objetivo = max(valor * 2, 1)

        paquetes.append({
            "campo": campo,
            "valor": valor,
            "objetivo": objetivo,
            "lbh_hex": hashlib.md5(f"{campo}{valor}".encode()).hexdigest()[:32],
            "sig": lbh_sig(f"{campo}|{valor}")
        })

    mision = {
        "video_id": video_id,
        "score": score,
        "adn_hex": hashlib.sha256(f"{video_id}|{ts}".encode()).hexdigest()[:32],
        "sig": lbh_sig(video_id)
    }

    return mision, paquetes, score

# ================================================================
# DB
# ================================================================

def inyectar_en_colonia(video_id, mision, paquetes):
    try:
        conn = sqlite3.connect(DB_COLONY)

        conn.execute("""
        INSERT INTO feromonas (nodo, payload, firma, ts)
        VALUES (?,?,?,?)
        """, (
            "TIKTOK-MISION",
            video_id,
            mision["sig"],
            int(time.time())
        ))

        for p in paquetes:
            conn.execute("""
            INSERT INTO feromonas (nodo, payload, firma, ts)
            VALUES (?,?,?,?)
            """, (
                f"TIKTOK-{p['campo']}",
                f"{p['valor']}->{p['objetivo']}",
                p["sig"],
                int(time.time())
            ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("[DB ERROR]", e)

# ================================================================
# SWARM
# ================================================================

def emitir_udp(adn):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(adn.encode(), ("127.0.0.1", UDP_PORT))
    sock.close()

# ================================================================
# REPORTE BONITO
# ================================================================

def generar_reporte(video_id, score, paquetes):
    print("\n📊 HORMIGASAIS REPORT")
    print("="*40)

    for p in paquetes:
        print(f"🐜 {p['campo'].upper()}")
        print(f"   {p['valor']} → {p['objetivo']}")
        print(f"   {p['lbh_hex'][:12]}...")
        print("-"*30)

    print(f"🔥 SCORE: {score}/999\n")

# ================================================================
# TRANSMUTADOR CENTRAL
# ================================================================

def procesar_url(url):
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

    emitir_udp(mision["adn_hex"])
    inyectar_en_colonia(video_id, mision, paquetes)
    generar_reporte(video_id, score, paquetes)

    print("[OK]", url)

# ================================================================
# WATCHER
# ================================================================

def watcher_loop():
    print("[WATCHER] activo...")
    seen = set()

    while True:
        try:
            if os.path.exists(WATCH_FILE):
                with open(WATCH_FILE) as f:
                    for line in f:
                        urls = re.findall(r"https://vt\.tiktok\.com/[A-Za-z0-9]+", line)
                        for url in urls:
                            if url not in seen:
                                seen.add(url)
                                print("[WATCH]", url)
                                procesar_url(url)
        except Exception as e:
            print("[WATCH ERROR]", e)

        time.sleep(5)

# ================================================================
# TELEGRAM
# ================================================================

def telegram_loop():
    print("[TELEGRAM] activo...")
    last_id = 0

    while True:
        try:
            r = requests.get(TELEGRAM_URL).json()

            for update in r.get("result", []):
                uid = update["update_id"]

                if uid <= last_id:
                    continue

                last_id = uid

                text = update.get("message", {}).get("text", "")

                if "tiktok.com" in text:
                    print("[TG]", text)
                    procesar_url(text)

        except Exception as e:
            print("[TG ERROR]", e)

        time.sleep(3)

# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":
    import threading

    t1 = threading.Thread(target=watcher_loop)
    t2 = threading.Thread(target=telegram_loop)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

