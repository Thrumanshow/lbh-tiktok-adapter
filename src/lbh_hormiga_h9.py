#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · HORMIGA H9 (EMISOR GEO MX)
# Soberanía: San Miguel decide | MX ejecuta
# ================================================================

import socket, json, time

# ================================================================
# CONFIG
# ================================================================

MX_NODE_IP = "45.167.2.139"   # ← CAMBIA ESTO
MX_NODE_PORT = 5005

NODE_ORIGIN = "A16-SanMiguel-SV"

# ================================================================
# GEO CONTEXTO (REFERENCIA, NO DECISIÓN)
# ================================================================

def contexto_geo():
    return {
        "region": "MX",
        "lat": 19.4326,
        "lon": -99.1332,
        "ciudad": "CDMX"
    }

# ================================================================
# EMISIÓN HACIA ENJAMBRE (MX OBEDECE)
# ================================================================

def emitir_a_mx(video_id, score, adn_hex):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        payload = {
            "type": "lbh_command",
            "node": NODE_ORIGIN,
            "video_id": video_id,
            "score": score,
            "lbh": adn_hex,
            "ts": int(time.time()),
            "geo_ref": contexto_geo()
        }

        sock.sendto(json.dumps(payload).encode(), (MX_NODE_IP, MX_NODE_PORT))

        print("🌎 H9 → enviado a MX")
        print(f"🎯 {video_id} | Score: {score}")

    except Exception as e:
        print("❌ Error emisión MX:", e)

# ================================================================
# INTERFAZ PARA LA REYNA
# ================================================================

def ejecutar_post_mision(video_id, score, adn_hex):
    print("🐜 H9 activo → propagando al enjambre")

    emitir_a_mx(video_id, score, adn_hex)

# ================================================================
# TEST
# ================================================================

if __name__ == "__main__":
    ejecutar_post_mision("TEST123", 10, "abc123def456")

