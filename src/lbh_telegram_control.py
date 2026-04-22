#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · REYNA v12.6 SOBERANA
# Nodo A16 · San Miguel, SV
# NUEVO: Puente feromona LBH → xoxo-lbh-adapter + colonia A16
# Sin romper H9/H10/Telegram/Contabilidad
# ================================================================
import os, time, json, sqlite3, hmac, hashlib, socket
import requests, subprocess
from threading import Thread
from datetime import datetime

# ── IDENTIDAD ────────────────────────────────────────────────
NODE_ID   = "A16-SanMiguel-SV"
VERSION   = "12.6"
HMAC_KEY  = b"hormigasais-sovereign-2026"
BOT_TOKEN = "8414322465:AAFgwr4ny4vN36rK3knCt3inJNzy-1xrVwU"
CHAT_ID   = "8463843180"
BASE_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── RUTAS ─────────────────────────────────────────────────────
LIBRO_MAYOR  = os.path.expanduser("~/lbh-tiktok-adapter/contabilidad_soberana.json")
DB_COLONY    = os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db")
DB_COLONY2   = os.path.expanduser("~/hormigasais-lab/lbh-node-service/lbh_nodo.db")
FEROMONA_LOG = os.path.expanduser("~/hormigasais-lab/logs/feromonas_reyna.log")
SWARM_LOG    = os.path.expanduser("~/hormigasais-lab/logs/tiktok_swarm.log")

for f in [FEROMONA_LOG, SWARM_LOG]:
    os.makedirs(os.path.dirname(f), exist_ok=True)

# ================================================================
# PUENTE DE FEROMONAS LBH (inyeccion quirurgica)
# ================================================================

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def json_to_lbh_packet(data: dict) -> str:
    import json as _json
    SECRET_KEY = b"hormigasais_secret_token_2025"
    json_str   = _json.dumps(data, separators=(",", ":"))
    payload_bytes = json_str.encode()
    sig = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
    full_packet = f"{json_str}|{sig}"
    return full_packet.encode().hex()

def emitir_feromona_lbh(video_id, evento, datos=None):
    ts  = int(time.time())
    sig = lbh_sig(f"{evento}|{video_id}|{ts}")

    payload_dict = {
        "type":      evento,
        "video_id":  video_id,
        "node":      NODE_ID,
        "sig":       sig,
        "ts":        ts,
    }
    if datos:
        payload_dict.update(datos)

    lbh_hex = json_to_lbh_packet(payload_dict)

    # 1. Colonia A16 SQLite
    for db in [DB_COLONY, DB_COLONY2]:
        try:
            conn   = sqlite3.connect(db)
            tablas = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
            if "feromonas" in tablas:
                conn.execute(
                    "INSERT INTO feromonas (nodo, payload, firma, ts) VALUES (?,?,?,?)",
                    (f"REYNA-{evento}", f"LBH://{evento}|{video_id}|v12.6", sig, ts)
                )
                conn.commit()
                conn.close()
                break
            conn.close()
        except Exception: pass

    # 2. Log swarm
    try:
        with open(SWARM_LOG, "a") as f:
            f.write(f"{ts}|{NODE_ID}|{evento}|{video_id}|sig:{sig}\n")
    except Exception: pass

    # 3. UDP bus (no bloqueante)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg  = f"LBH_PULSE|{evento}|{video_id}|{lbh_hex[:32]}".encode()
        sock.sendto(msg, ("127.0.0.1", 5005))
        sock.close()
    except Exception: pass

    # 4. Log feromona
    try:
        with open(FEROMONA_LOG, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{evento}|{video_id}|{sig}\n")
    except Exception: pass

    return sig, lbh_hex

# ================================================================
# TELEGRAM
# ================================================================

def send(msg):
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception: pass

def handle(chat_id, text):
    raw_text = text.strip()
    cmd      = raw_text.lower()

    if raw_text.startswith("/h9"):
        parts = raw_text.split(" ", 1)
        url   = parts[1].strip() if len(parts) > 1 else ""
        if not url:
            return send("Indique URL: `/h9 https://vt.tiktok.com/XXXXX/`")

        import re
        m = re.search(r"[vt|vm]\.tiktok\.com/([A-Za-z0-9]+)", url)
        video_id = m.group(1) if m else url.rstrip("/").split("/")[-1]

        send(f"[H9-AUTONOMO] Iniciando orquestacion para `{video_id}`...")
        sig_inicio, lbh_inicio = emitir_feromona_lbh(video_id, "H9_INICIO")

        h9_script = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h9_orquestador.py")
        try:
            subprocess.run(["python3", h9_script, url], timeout=60)
        except Exception: pass

        sig_fin, lbh_fin = emitir_feromona_lbh(video_id, "H9_COMPLETADO", {"url": url})
        send(f"Mision `{video_id}` completada\nFeromona LBH: `{sig_fin}`\nProcese con `/auditar {video_id}`")

    elif raw_text.startswith("/auditar"):
        parts = raw_text.split(" ", 1)
        vid   = parts[1].strip() if len(parts) > 1 else ""
        if not vid:
            return send("Indique el ID: `/auditar ZSHva7wnT`")

        h10_script = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h10_contadora.py")
        try:
            res = subprocess.check_output(["python3", h10_script, vid], timeout=30).decode().strip()
        except Exception as e: res = f"Error H10: {e}"

        sig_cont, _ = emitir_feromona_lbh(vid, "H10_AUDITORIA", {"resultado": res[:80]})
        send(f"AUDITORIA H10\n{res}\nSello LBH: `{sig_cont}`")

    elif cmd == "/balance":
        total, misiones = 0.0, 0
        if os.path.exists(LIBRO_MAYOR):
            with open(LIBRO_MAYOR) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        total += d.get("detalles", {}).get("utilidad_neta", 0.0)
                        misiones += 1
                    except: pass
        sig_bal, _ = emitir_feromona_lbh("BALANCE", "H10_BALANCE", {"total": total})
        send(f"BALANCE ACUMULADO\nUtilidad Neta: `${total:.4f}`\nMisiones: `{misiones}`\nSello: `{sig_bal}`")

    elif cmd == "/estado":
        feromonas = 0
        for db in [DB_COLONY, DB_COLONY2]:
            try:
                conn = sqlite3.connect(db)
                feromonas = conn.execute("SELECT COUNT(*) FROM feromonas").fetchone()[0]
                conn.close()
                break
            except: pass
        send(f"ESTADO DE LA REYNA v{VERSION}\n\nNodo: `{NODE_ID}`\nCerebro: `LBH-Core`\nColonia: `{feromonas:,} feromonas`\nConectividad: `Soberana`")

    elif cmd in ["/feromonas", "/f"]:
        try:
            lines = open(FEROMONA_LOG).readlines()[-5:]
            msg = "Ultimas feromonas LBH:\n" + "".join([f"  {l.strip()[:60]}\n" for l in lines])
            send(msg)
        except: send("Sin feromonas registradas aun")

    elif cmd == "/start":
        send(f"SISTEMA REYNA v{VERSION}\nNodo {NODE_ID}\n\n/h9 [URL] - Mision Viral\n/auditar [ID] - Sellar Contabilidad\n/balance - Ver Utilidades\n/estado - Salud del Nodo\n/feromonas - Ver bus LBH")

def listener():
    offset = None
    while True:
        try:
            r = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 20}).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                if "message" in u and "text" in u["message"]:
                    handle(str(u["message"]["chat"]["id"]), u["message"]["text"])
        except: time.sleep(3)

if __name__ == "__main__":
    print(f"REYNA v{VERSION} ONLINE - NODO {NODE_ID}")
    Thread(target=listener, daemon=True).start()
    try:
        while True: time.sleep(10)
    except KeyboardInterrupt: pass
