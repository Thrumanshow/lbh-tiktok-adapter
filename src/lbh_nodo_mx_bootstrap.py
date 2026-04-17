#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · NODO MX (BOOTSTRAP + LBH SOBERANO GEO)
# Nodo: MX-NODO-CDMX | Arquitectura: Listener + DB + Pulso
# ================================================================

import os, socket, json, sqlite3, time, hashlib, threading

# ================================================================
# CONFIGURACIÓN SOBERANA (RUTAS RELATIVAS)
# ================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKDIR  = os.path.join(BASE_DIR, ".colonia")
DB_PATH  = os.path.join(WORKDIR, "lbh_nodo_mx.db")

os.makedirs(WORKDIR, exist_ok=True)

UDP_IP   = "0.0.0.0"
UDP_PORT = 5005

NODE_NAME = "MX-NODO-CDMX"

# 🌎 GEO REAL (CDMX)
GEO_DATA = {
    "lat": 19.4326,
    "lon": -99.1332,
    "city": "Mexico City",
    "country": "MX"
}

PULSE_TARGET = ("127.0.0.1", 6000)

print("🧬 Inicializando nodo MX...")

# ================================================================
# VALIDACIÓN LBH (IDENTIDAD)
# ================================================================

def validar_nodo():
    try:
        seed = f"{socket.gethostname()}-{GEO_DATA['city']}"
        hash_id = hashlib.sha256(seed.encode()).hexdigest()[:12]

        print(f"🔐 Nodo validado: {hash_id}")
        return True
    except:
        return False

if not validar_nodo():
    print("❌ Nodo inválido")
    exit()

# ================================================================
# BASE DE DATOS (FEROMONAS GEO)
# ================================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS feromonas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nodo TEXT,
        lbh_payload TEXT,
        lat REAL,
        lon REAL,
        ts INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================================================================
# GUARDAR FEROMONA
# ================================================================

def guardar(data):
    try:
        conn = sqlite3.connect(DB_PATH)

        conn.execute("""
        INSERT INTO feromonas (nodo, lbh_payload, lat, lon, ts)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("node", NODE_NAME),
            data.get("lbh", "NULL"),
            GEO_DATA["lat"],
            GEO_DATA["lon"],
            int(time.time())
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("❌ DB ERROR:", e)

# ================================================================
# PULSO (HEARTBEAT DEL NODO)
# ================================================================

def emitir_pulso():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            msg = json.dumps({
                "type": "pulse",
                "node": NODE_NAME,
                "geo": [GEO_DATA["lat"], GEO_DATA["lon"]],
                "status": "alive",
                "ts": int(time.time())
            }).encode()

            sock.sendto(msg, PULSE_TARGET)

        except Exception as e:
            print("⚠️ Error pulso:", e)

        time.sleep(10)

# ================================================================
# LISTENER LBH (RECEPTOR GEO REAL)
# ================================================================

def listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"🌎 {NODE_NAME} activo en {GEO_DATA['city']}")
    print(f"📡 Escuchando UDP:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(2048)

        try:
            payload = json.loads(data.decode())

            lbh = payload.get("lbh", "N/A")

            print(f"🟢 {addr[0]} → {lbh[:12]}...")

            guardar(payload)

        except Exception as e:
            print("⚠️ Error payload:", e)

# ================================================================
# EJECUCIÓN PARALELA
# ================================================================

threading.Thread(target=emitir_pulso, daemon=True).start()
listener()

