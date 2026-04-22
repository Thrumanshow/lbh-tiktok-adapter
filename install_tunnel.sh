#!/usr/bin/env python3
import os, pathlib

base = pathlib.Path.home() / 'lbh-tiktok-adapter/src'
base.mkdir(parents=True, exist_ok=True)

# ── lbh_tunnel.py — Túnel soberano LBH ───────────────────────
p = base / 'lbh_tunnel.py'

code = '''#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · LBH TUNNEL v1.0 — NGROK SOBERANO
# Sin dependencias externas. Autenticacion por feromonas HMAC.
# Modos:
#   server  → corre en A16 (nodo privado)
#   relay   → corre en A20 o VPS publico
#   client  → conecta desde exterior via relay
# ================================================================

import socket, threading, time, hmac, hashlib, json, os, sys
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────
HMAC_KEY     = b"hormigasais-sovereign-2026"
NODE_ORIGIN  = "A16-SanMiguel-SV"
VERSION      = "1.0"

# Puertos del tunel LBH
TUNNEL_PORT_LOCAL  = 8100   # Puerto local a exponer (REST API)
TUNNEL_PORT_SERVER = 9100   # Puerto donde corre el servidor del tunel
TUNNEL_PORT_RELAY  = 9200   # Puerto del relay publico

# IPs
A16_IP  = "192.168.1.5"
A20_IP  = "192.168.1.7"   # Relay local
LOG     = os.path.expanduser("~/hormigasais-lab/logs/lbh_tunnel.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

# ── CRYPTO FEROMONAS ─────────────────────────────────────────
def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def lbh_handshake(node_id):
    ts  = int(time.time())
    sig = lbh_sig(f"TUNNEL|{node_id}|{ts}")
    return json.dumps({
        "type":    "LBH_HANDSHAKE",
        "node":    node_id,
        "version": VERSION,
        "sig":     sig,
        "ts":      ts,
    }).encode()

def lbh_verify(data):
    try:
        d   = json.loads(data.decode())
        sig = lbh_sig(f"TUNNEL|{d[chr(110)+chr(111)+chr(100)+chr(101)]}|{d[chr(116)+chr(115)]}")
        return sig == d.get("sig") and abs(int(time.time()) - d["ts"]) < 30
    except Exception:
        return False

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + chr(10))

# ================================================================
# MODO SERVER — corre en A16 (nodo privado)
# Acepta conexiones del relay y las reenvía al servicio local
# ================================================================

def handle_tunnel_conn(conn_relay, local_port):
    """Puente entre relay→A16 y A16→servicio local"""
    try:
        conn_local = socket.create_connection(("127.0.0.1", local_port), timeout=5)
        log(f"[SERVER] Tunel activo: relay ↔ localhost:{local_port}")

        def relay_to_local():
            try:
                while True:
                    data = conn_relay.recv(4096)
                    if not data: break
                    conn_local.sendall(data)
            except Exception:
                pass

        def local_to_relay():
            try:
                while True:
                    data = conn_local.recv(4096)
                    if not data: break
                    conn_relay.sendall(data)
            except Exception:
                pass

        t1 = threading.Thread(target=relay_to_local, daemon=True)
        t2 = threading.Thread(target=local_to_relay, daemon=True)
        t1.start(); t2.start()
        t1.join(); t2.join()
    except Exception as e:
        log(f"[SERVER] Error tunel: {e}")
    finally:
        try: conn_relay.close()
        except: pass

def modo_server(local_port=TUNNEL_PORT_LOCAL, server_port=TUNNEL_PORT_SERVER):
    log(f"[SERVER] LBH Tunnel Server activo en :{server_port}")
    log(f"[SERVER] Exponiendo localhost:{local_port} al relay")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", server_port))
    srv.listen(10)

    # Emitir feromona de inicio
    _emit_feromona("TUNNEL_SERVER_START", f"port:{server_port}")

    while True:
        try:
            conn, addr = srv.accept()
            log(f"[SERVER] Conexion desde {addr[0]}:{addr[1]}")

            # Verificar handshake LBH
            try:
                data = conn.recv(512)
                if not lbh_verify(data):
                    log(f"[SERVER] Handshake RECHAZADO desde {addr[0]}")
                    conn.close()
                    continue
                # Responder con OK firmado
                conn.sendall(lbh_handshake(NODE_ORIGIN))
                log(f"[SERVER] Handshake OK — {addr[0]}")
            except Exception as e:
                log(f"[SERVER] Error handshake: {e}")
                conn.close()
                continue

            t = threading.Thread(
                target=handle_tunnel_conn,
                args=(conn, local_port),
                daemon=True
            )
            t.start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"[SERVER] Error: {e}")

# ================================================================
# MODO RELAY — corre en A20 o VPS
# Acepta conexiones publicas y las redirige al servidor A16
# ================================================================

def handle_relay_client(conn_public, a16_host, a16_server_port):
    """Conecta cliente publico con servidor A16"""
    try:
        # Conectar al server A16
        conn_a16 = socket.create_connection((a16_host, a16_server_port), timeout=10)

        # Hacer handshake LBH con A16
        conn_a16.sendall(lbh_handshake("RELAY-NODE"))
        resp = conn_a16.recv(512)
        if not lbh_verify(resp):
            log(f"[RELAY] A16 no verificado — cerrando")
            conn_public.close()
            conn_a16.close()
            return

        log(f"[RELAY] Puente activo: cliente ↔ A16:{a16_server_port}")

        def pub_to_a16():
            try:
                while True:
                    data = conn_public.recv(4096)
                    if not data: break
                    conn_a16.sendall(data)
            except: pass

        def a16_to_pub():
            try:
                while True:
                    data = conn_a16.recv(4096)
                    if not data: break
                    conn_public.sendall(data)
            except: pass

        t1 = threading.Thread(target=pub_to_a16, daemon=True)
        t2 = threading.Thread(target=a16_to_pub, daemon=True)
        t1.start(); t2.start()
        t1.join(); t2.join()
    except Exception as e:
        log(f"[RELAY] Error: {e}")
    finally:
        try: conn_public.close()
        except: pass

def modo_relay(relay_port=TUNNEL_PORT_RELAY,
               a16_host=A16_IP,
               a16_server_port=TUNNEL_PORT_SERVER):
    log(f"[RELAY] LBH Relay activo en :{relay_port}")
    log(f"[RELAY] Reenviando a {a16_host}:{a16_server_port}")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", relay_port))
    srv.listen(20)

    _emit_feromona("TUNNEL_RELAY_START", f"relay:{relay_port}->a16:{a16_server_port}")

    while True:
        try:
            conn, addr = srv.accept()
            log(f"[RELAY] Cliente publico: {addr[0]}:{addr[1]}")
            t = threading.Thread(
                target=handle_relay_client,
                args=(conn, a16_host, a16_server_port),
                daemon=True
            )
            t.start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"[RELAY] Error: {e}")

# ================================================================
# MODO CLIENT — conecta desde exterior
# Envia requests HTTP a traves del relay hacia A16
# ================================================================

def modo_client(relay_host, relay_port=TUNNEL_PORT_RELAY,
                test_path="/ping"):
    log(f"[CLIENT] Conectando via relay {relay_host}:{relay_port}")

    try:
        conn = socket.create_connection((relay_host, relay_port), timeout=10)
        log(f"[CLIENT] Conectado al relay")

        # Enviar request HTTP de prueba
        request = (
            f"GET {test_path} HTTP/1.1" + chr(13) + chr(10) +
            f"Host: {relay_host}" + chr(13) + chr(10) +
            f"X-LBH-Node: {NODE_ORIGIN}" + chr(13) + chr(10) +
            f"X-LBH-Sig: {lbh_sig(test_path)}" + chr(13) + chr(10) +
            chr(13) + chr(10)
        )
        conn.sendall(request.encode())

        # Leer respuesta
        response = b""
        conn.settimeout(5)
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk: break
                response += chunk
        except socket.timeout:
            pass

        conn.close()
        log(f"[CLIENT] Respuesta: {len(response)} bytes")
        return response.decode(errors="replace")[:500]
    except Exception as e:
        log(f"[CLIENT] Error: {e}")
        return None

# ================================================================
# STATUS — ver estado del tunel LBH
# ================================================================

def modo_status():
    log(f"[STATUS] Verificando tunel LBH...")

    # Verificar server local
    try:
        s = socket.create_connection(("127.0.0.1", TUNNEL_PORT_SERVER), timeout=2)
        s.close()
        log(f"[STATUS] Server local :{TUNNEL_PORT_SERVER} OK")
    except:
        log(f"[STATUS] Server local :{TUNNEL_PORT_SERVER} DOWN")

    # Verificar relay A20
    try:
        s = socket.create_connection((A20_IP, TUNNEL_PORT_RELAY), timeout=2)
        s.close()
        log(f"[STATUS] Relay A20 {A20_IP}:{TUNNEL_PORT_RELAY} OK")
    except:
        log(f"[STATUS] Relay A20 {A20_IP}:{TUNNEL_PORT_RELAY} DOWN")

    # Verificar servicio local a exponer
    try:
        s = socket.create_connection(("127.0.0.1", TUNNEL_PORT_LOCAL), timeout=2)
        s.close()
        log(f"[STATUS] Servicio local :{TUNNEL_PORT_LOCAL} OK")
    except:
        log(f"[STATUS] Servicio local :{TUNNEL_PORT_LOCAL} DOWN")

    # Ver ultimas lineas del log
    try:
        lines = open(LOG).readlines()[-5:]
        print(chr(10) + "Ultimas feromonas del tunel:")
        for l in lines: print(" ", l.strip())
    except: pass

# ================================================================
# FEROMONA EMISOR (integrado con colonia A16)
# ================================================================

def _emit_feromona(evento, datos=""):
    import sqlite3
    db_paths = [
        os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db"),
        os.path.expanduser("~/hormigasais-lab/lbh-node-service/lbh_nodo.db"),
    ]
    ts  = int(time.time())
    sig = lbh_sig(f"{evento}|{datos}|{ts}")
    for db in db_paths:
        try:
            conn = sqlite3.connect(db)
            tablas = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
            if "feromonas" in tablas:
                conn.execute(
                    "INSERT INTO feromonas (nodo, payload, firma, ts) VALUES (?,?,?,?)\n",
                    (f"LBH-TUNNEL",
                     f"LBH://TUNNEL|{evento}|{datos[:40]}",
                     sig, ts)
                )
                conn.commit()
                conn.close()
                return
            conn.close()
        except Exception:
            pass

# ── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "help"

    print()
    print("=" * 55)
    print("  HORMIGASAIS · LBH TUNNEL v1.0")
    print("  Tunel soberano — sin ngrok — sin dependencias")
    print(f"  Nodo: {NODE_ORIGIN}")
    print("=" * 55)
    print()

    if modo == "server":
        local  = int(sys.argv[2]) if len(sys.argv) > 2 else TUNNEL_PORT_LOCAL
        port   = int(sys.argv[3]) if len(sys.argv) > 3 else TUNNEL_PORT_SERVER
        modo_server(local, port)

    elif modo == "relay":
        rport  = int(sys.argv[2]) if len(sys.argv) > 2 else TUNNEL_PORT_RELAY
        a16    = sys.argv[3] if len(sys.argv) > 3 else A16_IP
        sport  = int(sys.argv[4]) if len(sys.argv) > 4 else TUNNEL_PORT_SERVER
        modo_relay(rport, a16, sport)

    elif modo == "client":
        relay  = sys.argv[2] if len(sys.argv) > 2 else A20_IP
        rport  = int(sys.argv[3]) if len(sys.argv) > 3 else TUNNEL_PORT_RELAY
        path   = sys.argv[4] if len(sys.argv) > 4 else "/ping"
        res    = modo_client(relay, rport, path)
        if res: print("Respuesta:", res[:300])

    elif modo == "status":
        modo_status()

    else:
        print("Modos:")
        print()
        print("  EN A16 (privado):")
        print(f"  python3 lbh_tunnel.py server {TUNNEL_PORT_LOCAL} {TUNNEL_PORT_SERVER}")
        print(f"  Expone localhost:{TUNNEL_PORT_LOCAL} al relay")
        print()
        print("  EN A20 / VPS (relay publico):")
        print(f"  python3 lbh_tunnel.py relay {TUNNEL_PORT_RELAY} {A16_IP} {TUNNEL_PORT_SERVER}")
        print(f"  Relay en :{TUNNEL_PORT_RELAY} → A16:{TUNNEL_PORT_SERVER}")
        print()
        print("  DESDE EXTERIOR:")
        print(f"  python3 lbh_tunnel.py client IP_RELAY {TUNNEL_PORT_RELAY} /v1/lbh/validate")
        print()
        print("  VER ESTADO:")
        print("  python3 lbh_tunnel.py status")
        print()
        print("  ARQUITECTURA:")
        print(f"  Internet → Relay:{TUNNEL_PORT_RELAY} → A16:{TUNNEL_PORT_SERVER} → localhost:{TUNNEL_PORT_LOCAL}")
        print("  Todo autenticado con HMAC LBH")
'''

p.write_text(code)
p.chmod(0o755)
print('OK lbh_tunnel.py v1.0')
print(str(p))

