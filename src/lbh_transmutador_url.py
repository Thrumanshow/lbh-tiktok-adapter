#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · TRANSMUTADOR URL→FEROMONAS v1.0
# ================================================================

import sqlite3, os, time, hmac, hashlib, json, re, socket
from datetime import datetime

HMAC_KEY    = b"hormigasais-sovereign-2026"
NODE_ORIGIN = "A16-SanMiguel-SV"
UDP_PORT    = 5005

DB_COLONY   = os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db")

# ================================================================
# FEROMONAS TIPOS
# ================================================================

FEROMONA_TIPOS = {
    "URL_BASE": 0x01,
    "ENGAGEMENT": 0x03,
    "MISSION": 0x07,
}

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def url_to_lbh_binary(url):
    url_bytes = hashlib.md5(url.encode()).digest()[:4]
    ts = int(time.time())

    score = min(999, (len(url) * 3) % 100)

    lbh_packet = (
        format(FEROMONA_TIPOS["URL_BASE"], "02x") +
        url_bytes.hex() +
        format(ts & 0xFFFFFFFF, "08x") +
        format(score, "04x")
    )

    return lbh_packet[:32], score

def extraer_video_id(url):
    m = re.search(r"vt\.tiktok\.com/([A-Za-z0-9]+)", url)
    return m.group(1) if m else url.split("/")[-1]

# ================================================================
# METRICAS
# ================================================================

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
# SWARM
# ================================================================

def emitir_al_swarm_udp(lbh_hex):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(lbh_hex.encode(), ("127.0.0.1", UDP_PORT))
    sock.close()

# ================================================================
# DB (CORREGIDO)
# ================================================================

def inyectar_en_colonia(video_id, mision, paquetes):
    try:
        conn = sqlite3.connect(DB_COLONY)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS feromonas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nodo TEXT,
            payload TEXT,
            firma TEXT,
            ts INTEGER
        )
        """)

        # Inserta misión
        conn.execute("""
        INSERT INTO feromonas (nodo, payload, firma, ts)
        VALUES (?,?,?,?)
        """, (
            "TIKTOK-MISION",
            video_id,
            mision["sig"],
            int(time.time())
        ))

        # Inserta métricas
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
        return True

    except Exception as e:
        print("DB error:", e)
        return False

# ================================================================
# REPORTE
# ================================================================

def generar_reporte_transmutacion(video_id, url, score, url_lbh, mision_lbh, plan):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# Transmutacion LBH — {video_id}

URL: {url}
Fecha: {ahora}
Nodo: {NODE_ORIGIN}
Score: {score}/999
URL→LBH: {url_lbh}
ADN: {mision_lbh['adn_hex']}
Firma: {mision_lbh['sig']}

---

Plan:

"""

    for item in plan:
        md += f"{item['campo']} {item['actual']}->{item['objetivo']}\n"

    return md

# ================================================================
# CORE
# ================================================================

def transmutacion_completa(url, metricas):
    video_id = extraer_video_id(url)

    url_lbh, _ = url_to_lbh_binary(url)
    mision, paquetes, score = metricas_to_feromonas(video_id, metricas)

    emitir_al_swarm_udp(mision["adn_hex"])
    inyectar_en_colonia(video_id, mision, paquetes)

    print("OK:", video_id, score)

# ================================================================
# ENTRYPOINT
# ================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 8:
        url = sys.argv[1]

        metricas = {
            "views": int(sys.argv[2]),
            "likes": int(sys.argv[3]),
            "comments": int(sys.argv[4]),
            "saves": int(sys.argv[5]),
            "shares": int(sys.argv[6]),
            "purchases": int(sys.argv[7])
        }

        transmutacion_completa(url, metricas)

    else:
        url = input("URL: ")
        metricas = {
            "views": int(input("views: ") or 0),
            "likes": int(input("likes: ") or 0),
            "comments": int(input("comments: ") or 0),
            "saves": int(input("saves: ") or 0),
            "shares": int(input("shares: ") or 0),
            "purchases": int(input("purchases: ") or 0),
        }

        transmutacion_completa(url, metricas)

