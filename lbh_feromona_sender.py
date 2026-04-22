#!/usr/bin/env python3
import socket, json, hmac, hashlib, time, os, sys
from datetime import datetime

# CONFIGURACIÓN SOBERANA
A20_IP   = "192.168.1.5"  # Cambia a la IP real del A20 si no es local
A20_PORT = 9200
HMAC_KEY = b"hormigasais-sovereign-2026"
NODE_ID  = "A16-SanMiguel-SV"
LOG_FILE = os.path.expanduser("~/hormigasais-lab/logs/feromona_sender.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def lbh_sig(p):
    return hmac.new(HMAC_KEY, p.encode(), hashlib.sha256).hexdigest()[:16]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [SENDER] {NODE_ID} >> {msg}"
    print(line)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def emitir_feromona(v_id, sc, cat):
    ts = int(time.time())
    # Contrato de datos para la firma
    check_str = f"FEROMONA|{v_id}|{sc}|{cat}|{ts}"
    feromona = {
        "type": "FEROMONA",
        "video_id": v_id,
        "score": sc,
        "categoria": cat,
        "nodo": NODE_ID,
        "sig": lbh_sig(check_str),
        "ts": ts
    }

    log(f"Emitiendo a {A20_IP}:{A20_PORT} | video={v_id} sig={feromona['sig']}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((A20_IP, A20_PORT))
        s.sendall(json.dumps(feromona).encode("utf-8"))
        
        resp_raw = s.recv(1024)
        if resp_raw:
            log(f"ACK RECIBIDO: {resp_raw.decode()}")
            return True
        s.close()
    except Exception as e:
        log(f"Falla en el túnel: {e}")
        return False

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "TEST_001"
    score = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    categoria = sys.argv[3] if len(sys.argv) > 3 else "VIRAL"
    emitir_feromona(vid, score, categoria)
