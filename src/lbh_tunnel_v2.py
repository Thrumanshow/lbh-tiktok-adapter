#!/usr/bin/env python3
# ===========================================================
# HORMIGASAIS - LBH TUNNEL v2.0 (PURIFICADO)
# ===========================================================
import socket, threading, time, hmac, hashlib, json, os, sys, struct
from datetime import datetime

HMAC_KEY = b"hormigasais-sovereign-2026"
CLHQ_KEY = b"clhq-firma-maestra-colonia"
VERSION = "2.0"
NODE_ID = os.getenv("NODE_ID", "A16-Reyna-SV")
A16_IP = "192.168.1.5"
A20_IP = "192.168.1.6"
A16_PORT = 9100
REL_PORT = 9200
UDP_XOXO = 5006
UDP_BUS = 5005

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {NODE_ID} >> {msg}")

def lbh_sig(payload, key=HMAC_KEY):
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()[:16]

def clhq_sig(payload):
    return lbh_sig(payload, key=CLHQ_KEY)

def mk_handshake(node_id, role="TUNNEL"):
    ts = int(time.time())
    sig = lbh_sig(f"{role}|{node_id}|{ts}")
    return json.dumps({"type":"LBH_HANDSHAKE","role":role,"node":node_id,"sig":sig,"ts":ts}).encode()

def mk_xoxo_feromona(mision_id, origen, destino, tipo="VALIDACION"):
    ts = int(time.time())
    payload = f"XOXO|{tipo}|{mision_id}|{origen}|{destino}|{ts}"
    return json.dumps({
        "type": "XOXO_FEROMONA", "subtipo": tipo, "mision": mision_id,
        "origen": origen, "destino": destino, "ts": ts,
        "sig_lbh": lbh_sig(payload), "sig_clhq": clhq_sig(payload)
    }).encode()

def verify_handshake(data):
    try:
        d = json.loads(data.decode())
        return lbh_sig(f"{d['role']}|{d['node']}|{d['ts']}") == d['sig']
    except: return False

def verify_xoxo(d):
    try:
        payload = f"XOXO|{d['subtipo']}|{d['mision']}|{d['origen']}|{d['destino']}|{d['ts']}"
        return lbh_sig(payload) == d['sig_lbh'] and clhq_sig(payload) == d['sig_clhq']
    except: return False

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data: break
            dst.sendall(data)
    except: pass

def modo_server(server_port, local_port):
    log(f"Reyna activa en :{server_port}")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", server_port))
    srv.listen(20)
    while True:
        try:
            conn, addr = srv.accept()
            # Lógica de túnel aquí...
        except: pass

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "test"
    if modo == "test":
        pkt = json.loads(mk_xoxo_feromona("M-001", "A16", "A20", "VALIDACION").decode())
        print(f"LBH_SIG: {pkt['sig_lbh']}\nCLHQ_SIG: {pkt['sig_clhq']}")
        print(f"Status: {'VALIDO' if verify_xoxo(pkt) else 'ERROR'}")
    elif modo == "server":
        modo_server(A16_PORT, 8100)
