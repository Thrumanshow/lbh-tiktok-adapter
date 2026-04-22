#!/bin/bash
# -*- coding: utf-8 -*-
# ================================================================
# 🐜 HORMIGASAIS · FIX A16
# Cabos sueltos: hex_signal + cola + feromona → A20
# ================================================================

echo "🐜 [A16] Aplicando correcciones..."

# ── FIX 1: {hex_signal} como f-string en main_swarm.py ─────────
FILE=~/lbh-tiktok-adapter/main_swarm.py

if grep -q '"🧬 Generando ADN LBH: {hex_signal}"' "$FILE"; then
    sed -i 's/"🧬 Generando ADN LBH: {hex_signal}"/f"🧬 Generando ADN LBH: {hex_signal}"/' "$FILE"
    echo "✅ FIX 1: hex_signal corregido a f-string"
else
    echo "⚠️  FIX 1: línea no encontrada con ese patrón exacto"
    echo "   → Busca manualmente: grep -n 'hex_signal' ~/lbh-tiktok-adapter/main_swarm.py"
fi

# ── FIX 2: Crear estructura de cola si no existe ────────────────
mkdir -p ~/lbh-queue/inbox
mkdir -p ~/lbh-queue/processing
mkdir -p ~/lbh-queue/done
mkdir -p ~/lbh-queue/failed
echo "✅ FIX 2: Directorios de cola creados"

# ── FIX 3: lbh_feromona_sender.py ──────────────────────────────
# Envía la feromona al A20 vía socket después de cada ingestión
cat << 'PYEOF' > ~/lbh-tiktok-adapter/lbh_feromona_sender.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================================
# 🐜 HORMIGASAIS · FEROMONA SENDER
# Envía señal LBH del A16 → A20 vía socket
# ================================================================

import socket
import json
import os
from datetime import datetime

A20_HOST = "localhost"   # Cambia a IP real del A20 si es red local
A20_PORT = 9200
TIMEOUT  = 5

def enviar_feromona(video_id, score, categoria, hex_signal, nodo="A16-SanMiguel-SV"):
    payload = {
        "type":      "FEROMONA",
        "video_id":  video_id,
        "score":     score,
        "categoria": categoria,
        "signal":    hex_signal,
        "nodo":      nodo,
        "ts":        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((A20_HOST, A20_PORT))
        s.sendall(json.dumps(payload).encode("utf-8"))
        s.close()
        print(f"📡 [FEROMONA] Enviada → A20:{A20_PORT} | {video_id} | {categoria} | {score}")
        return True
    except Exception as e:
        print(f"⚠️  [FEROMONA] No se pudo conectar al A20: {e}")
        print(f"   → Feromona guardada localmente en cola")
        _guardar_local(payload)
        return False

def _guardar_local(payload):
    inbox = os.path.expanduser("~/lbh-queue/inbox")
    os.makedirs(inbox, exist_ok=True)
    fname = os.path.join(inbox, f"{payload['signal']}.json")
    with open(fname, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"💾 [COLA] Guardado: {fname}")

if __name__ == "__main__":
    # Test rápido
    enviar_feromona(
        video_id  = "TEST001",
        score     = 500,
        categoria = "VIRAL",
        hex_signal= "abcdef1234567890"
    )
PYEOF

echo "✅ FIX 3: lbh_feromona_sender.py creado"

# ── FIX 4: Patch en main_swarm.py para llamar al sender ────────
# Busca si ya tiene el import del sender
if grep -q "lbh_feromona_sender" "$FILE"; then
    echo "✅ FIX 4: sender ya integrado en main_swarm.py"
else
    echo ""
    echo "══════════════════════════════════════════════"
    echo "  ⚠️  FIX 4 MANUAL REQUERIDO"
    echo "══════════════════════════════════════════════"
    echo ""
    echo "  Agrega esto en main_swarm.py después del"
    echo "  bloque donde se genera hex_signal:"
    echo ""
    echo "  from lbh_feromona_sender import enviar_feromona"
    echo ""
    echo "  Y después del print del resumen:"
    echo ""
    echo "  enviar_feromona(video_id, score, categoria, hex_signal)"
    echo ""
    echo "  → Línea exacta buscar con:"
    echo "    grep -n 'hex_signal\|Resumen\|señal' $FILE"
    echo ""
fi

# ── RESUMEN ─────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "  ✅ FIX A16 APLICADO"
echo "════════════════════════════════════════"
echo ""
echo "▶ Test feromona sender:"
echo "  python3 ~/lbh-tiktok-adapter/lbh_feromona_sender.py"
echo ""
echo "▶ Ver cola:"
echo "  ls ~/lbh-queue/inbox/"
echo ""
echo "🐜 HormigasAIS · San Miguel, El Salvador · 2026"
