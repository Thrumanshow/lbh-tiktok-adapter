#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · LBH TUNNEL v1.1 — NGROK SOBERANO + GUARDIAN
# ================================================================

import socket, threading, time, hmac, hashlib, json, os, sys, subprocess
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────
HMAC_KEY     = b"hormigasais-sovereign-2026"
NODE_ORIGIN  = "A16-SanMiguel-SV"
VERSION      = "1.1"

TUNNEL_PORT_LOCAL  = 8100
TUNNEL_PORT_SERVER = 9100
TUNNEL_PORT_RELAY  = 9200

A16_IP  = "192.168.1.5"
A20_IP  = "192.168.1.7"

LOG = os.path.expanduser("~/hormigasais-lab/logs/lbh_tunnel.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

# ── CRYPTO ────────────────────────────────────────────────────
def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def lbh_handshake(node_id):
    ts  = int(time.time())
    sig = lbh_sig(f"TUNNEL|{node_id}|{ts}")
    return json.dumps({
        "type": "LBH_HANDSHAKE",
        "node": node_id,
        "version": VERSION,
        "sig": sig,
        "ts": ts
    }).encode()

def lbh_verify(data):
    try:
        d = json.loads(data.decode())
        sig = lbh_sig(f"TUNNEL|{d['node']}|{d['ts']}")
        return sig == d.get("sig") and abs(int(time.time()) - d["ts"]) < 30
    except:
        return False

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

# ================================================================
# SERVER (A16)
# ================================================================

def handle_tunnel_conn(conn_relay, local_port):
    try:
        conn_local = socket.create_connection(("127.0.0.1", local_port), timeout=5)
        log(f"[SERVER] Tunel activo ↔ localhost:{local_port}")

        def a():
            try:
                while True:
                    data = conn_relay.recv(4096)
                    if not data: break
                    conn_local.sendall(data)
            except: pass

        def b():
            try:
                while True:
                    data = conn_local.recv(4096)
                    if not data: break
                    conn_relay.sendall(data)
            except: pass

        threading.Thread(target=a, daemon=True).start()
        threading.Thread(target=b, daemon=True).start()

    except Exception as e:
        log(f"[SERVER] Error: {e}")

def modo_server(local_port, server_port):
    log(f"[SERVER] Activo en :{server_port}")
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", server_port))
    srv.listen(10)

    while True:
        try:
            conn, addr = srv.accept()
            data = conn.recv(512)
            if not lbh_verify(data):
                conn.close()
                continue
            conn.sendall(lbh_handshake(NODE_ORIGIN))
            threading.Thread(target=handle_tunnel_conn, args=(conn, local_port), daemon=True).start()
        except KeyboardInterrupt: break
        except Exception as e: log(f"[SERVER] Loop error: {e}")

# ================================================================
# RELAY (A20 / VPS)
# ================================================================

def handle_relay_client(conn_public, a16_host, a16_port):
    try:
        conn_a16 = socket.create_connection((a16_host, a16_port), timeout=10)
        conn_a16.sendall(lbh_handshake("RELAY"))
        if not lbh_verify(conn_a16.recv(512)):
            return

        def a():
            try:
                while True:
                    d = conn_public.recv(4096)
                    if not d: break
                    conn_a16.sendall(d)
            except: pass

        def b():
            try:
                while True:
                    d = conn_a16.recv(4096)
                    if not d: break
                    conn_public.sendall(d)
            except: pass

        threading.Thread(target=a, daemon=True).start()
        threading.Thread(target=b, daemon=True).start()
    except Exception as e:
        log(f"[RELAY] Error: {e}")

def modo_relay(port, a16, server_port):
    log(f"[RELAY] Activo :{port}")
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(20)

    while True:
        try:
            conn, addr = srv.accept()
            threading.Thread(target=handle_relay_client, args=(conn, a16, server_port), daemon=True).start()
        except KeyboardInterrupt: break
        except Exception as e: log(f"[RELAY] Loop error: {e}")

# ================================================================
# GUARDIAN (KEEPALIVE + RECONEXIÓN)
# ================================================================

def check_relay():
    try:
        s = socket.create_connection((A20_IP, TUNNEL_PORT_RELAY), timeout=2)
        s.close()
        return True
    except: return False

def start_relay():
    log("[GUARDIAN] 🚀 Lanzando relay...")
    # Se lanza a sí mismo en modo relay
    subprocess.Popen([sys.executable, __file__, "relay", str(TUNNEL_PORT_RELAY), A16_IP, str(TUNNEL_PORT_SERVER)])

def modo_guardian():
    log("[GUARDIAN] 🐜 Iniciado")
    retries = 0
    while True:
        try:
            if check_relay():
                if retries > 0: log("[GUARDIAN] 💓 Relay recuperado")
                retries = 0
            else:
                log("[GUARDIAN] ⚠️ Relay caído")
                if retries < 5:
                    start_relay()
                    retries += 1
                    log(f"[GUARDIAN] 🔁 Intento {retries}")
                    time.sleep(3)
                else:
                    log("[GUARDIAN] ❌ Max retries. Esperando 30s...")
                    retries = 0
                    time.sleep(30)
            time.sleep(10)
        except KeyboardInterrupt: break

# ================================================================
# MAIN
# ================================================================

def modo_status():
    log("[STATUS] Verificando infraestructura...")
    for label, ip, port in [("SERVER (A16)", "127.0.0.1", TUNNEL_PORT_SERVER), 
                             ("RELAY (A20)", A20_IP, TUNNEL_PORT_RELAY),
                             ("TIKTOK API", "127.0.0.1", TUNNEL_PORT_LOCAL)]:
        try:
            socket.create_connection((ip, port), timeout=2).close()
            print(f"  {label}: OK")
        except: print(f"  {label}: DOWN")

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "help"
    print(f"\n=== LBH TUNNEL {VERSION} ===")

    if modo == "server":
        modo_server(TUNNEL_PORT_LOCAL, TUNNEL_PORT_SERVER)
    elif modo == "relay":
        p = int(sys.argv[2]); a = sys.argv[3]; sp = int(sys.argv[4])
        modo_relay(p, a, sp)
    elif modo == "guardian":
        modo_guardian()
    elif modo == "status":
        modo_status()
    else:
        print("Uso: python3 lbh_tunnel.py [server|relay|guardian|status]")
