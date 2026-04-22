#!/usr/bin/env python3
import socket, json, hmac, hashlib
from datetime import datetime

PORT = 9300
HOST = '0.0.0.0'
HMAC_KEY = b'hormigasais-sovereign-2026'

def lbh_sig(p):
    return hmac.new(HMAC_KEY, p.encode(), hashlib.sha256).hexdigest()[:16]

def main():
    print(f"👑 Master A16 Escuchando Retornos en puerto {PORT}...")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((HOST, PORT))
        srv.listen(5)
    except Exception as e:
        print(f"Error de Bind en Master: {e}")
        return

    while True:
        try:
            conn, addr = srv.accept()
            raw = conn.recv(4096)
            if not raw: conn.close(); continue
            
            data = json.loads(raw.decode('utf-8'))
            v_id, sc, ts = data.get('video_id'), data.get('score'), data.get('ts')
            
            # Validación de autenticidad LBH
            check_str = f"RETORNO|{v_id}|{sc}|{ts}"
            if lbh_sig(check_str) == data.get('sig'):
                ts_lectura = datetime.now().strftime('%H:%M:%S')
                print(f"💎 [{ts_lectura}] [HITO RECIBIDO] Nodo {data.get('origen')} reporta: {v_id} (Score: {sc})")
            else:
                print("⚠️ Intento de conexión con firma inválida.")
            conn.close()
        except Exception as e:
            print(f"Error en recepción: {e}")

if __name__ == "__main__":
    main()
