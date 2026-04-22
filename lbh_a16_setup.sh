#!/bin/bash
# -*- coding: utf-8 -*-
# ================================================================
# 🐜 HORMIGASAIS · SETUP COMPLETO A16
# Rutas, supervisor, métricas, queue
# ================================================================

echo "🐜 Iniciando setup A16..."

# ── 1. CREAR DIRECTORIOS NECESARIOS ──────────────────────────
mkdir -p ~/lbh-queue/inbox
mkdir -p ~/lbh-queue/processing
mkdir -p ~/lbh-queue/done
mkdir -p ~/lbh-queue/failed
mkdir -p ~/lbh-metrics
mkdir -p ~/hormigasais-lab/logs

echo "✅ Directorios creados"

# ── 2. SUPERVISOR ─────────────────────────────────────────────
cat << 'PYEOF' > ~/lbh-supervisor.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================================
# 🐜 HORMIGASAIS · SUPERVISOR v1.0
# ================================================================

import subprocess
import time
import os
from datetime import datetime

CHECK_INTERVAL = 5

PROCESOS = {
    "queue": {
        "cmd": ["python3", "lbh_queue_manager.py"],
        "path": os.path.expanduser("~/lbh-queue"),
    },
    "orchestrator": {
        "cmd": ["python3", "lbh_orchestrator.py"],
        "path": os.path.expanduser("~/lbh-compresion-adapter-video"),
    },
}

LOG_PATH = os.path.expanduser("~/hormigasais-lab/logs/supervisor.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

running = {}

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [SUPERVISOR] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def start_process(name, cfg):
    try:
        p = subprocess.Popen(
            cfg["cmd"],
            cwd=cfg["path"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        running[name] = p
        log(f"🚀 {name} iniciado (PID {p.pid})")
    except Exception as e:
        log(f"❌ Error iniciando {name}: {e}")

def check_process(name, cfg):
    p = running.get(name)
    if p is None:
        log(f"⚠️  {name} no registrado → iniciando...")
        start_process(name, cfg)
        return
    if p.poll() is not None:
        log(f"💀 {name} murió → reiniciando...")
        start_process(name, cfg)

def main():
    log("🐜 Supervisor iniciado")
    for name, cfg in PROCESOS.items():
        start_process(name, cfg)
    while True:
        try:
            for name, cfg in PROCESOS.items():
                check_process(name, cfg)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log("🛑 Supervisor detenido")
            break
        except Exception as e:
            log(f"❌ Error loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
PYEOF

echo "✅ Supervisor creado: ~/lbh-supervisor.py"

# ── 3. MÉTRICAS ───────────────────────────────────────────────
cat << 'PYEOF' > ~/lbh-metrics/lbh_metrics.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================================
# 🐜 HORMIGASAIS · METRICS v1.0
# ================================================================

import os, json, sys
from datetime import datetime

BASE_PATH = os.path.expanduser("~/hormigasais-lab/metrics")
LOG_PATH  = os.path.join(BASE_PATH, "metrics.log")
DB_PATH   = os.path.join(BASE_PATH, "metrics.json")

os.makedirs(BASE_PATH, exist_ok=True)

def load_state():
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            return json.load(f)
    return {
        "total_events": 0,
        "pipeline_ok": 0,
        "pipeline_fail": 0,
        "compression_ok": 0,
        "distribution_ok": 0,
        "publication_ok": 0,
        "last_event": None
    }

def save(state):
    with open(DB_PATH, "w") as f:
        json.dump(state, f, indent=2)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    line = f"[{now()}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def record(event_type):
    state = load_state()
    state["total_events"] += 1
    state["last_event"] = now()
    mapping = {
        "PIPELINE_OK":    "pipeline_ok",
        "PIPELINE_FAIL":  "pipeline_fail",
        "COMPRESION_OK":  "compression_ok",
        "DISTRIBUCION_OK":"distribution_ok",
        "PUBLICACION_OK": "publication_ok",
    }
    key = mapping.get(event_type)
    if key:
        state[key] += 1
    log(f"[METRICS] → {event_type}")
    save(state)

def summary():
    state = load_state()
    print("\n══════════════════════════════════════")
    print("  🐜 HORMIGASAIS · METRICS DASHBOARD")
    print("══════════════════════════════════════")
    print(f"📊 Total eventos:     {state['total_events']}")
    print(f"✅ Pipeline OK:       {state['pipeline_ok']}")
    print(f"❌ Pipeline FAIL:     {state['pipeline_fail']}")
    print(f"🎬 Compresión OK:     {state['compression_ok']}")
    print(f"📦 Distribución OK:   {state['distribution_ok']}")
    print(f"📡 Publicación OK:    {state['publication_ok']}")
    print(f"🕒 Último evento:     {state['last_event']}")
    print("══════════════════════════════════════\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 lbh_metrics.py record EVENTO")
        print("  python3 lbh_metrics.py summary")
        exit(1)
    if sys.argv[1] == "record" and len(sys.argv) > 2:
        record(sys.argv[2])
    elif sys.argv[1] == "summary":
        summary()
    else:
        print("Comando inválido")
PYEOF

echo "✅ Métricas creadas: ~/lbh-metrics/lbh_metrics.py"

# ── 4. FIX: {hex_signal} placeholder en main_swarm.py ────────
# Verifica si el bug del placeholder existe
if grep -q '"{hex_signal}"' ~/lbh-tiktok-adapter/main_swarm.py 2>/dev/null; then
    echo "⚠️  Bug detectado: {hex_signal} como string literal"
    echo "👉 Abre main_swarm.py y busca la línea con {hex_signal}"
    echo "   Debe ser: print(f\"🧬 Generando ADN LBH: {hex_signal}\")"
    echo "   (con la f antes de las comillas)"
else
    echo "✅ hex_signal OK (o main_swarm.py no encontrado en esta ruta)"
fi

# ── 5. PERMISOS ───────────────────────────────────────────────
chmod +x ~/lbh-supervisor.py
chmod +x ~/lbh-metrics/lbh_metrics.py

echo ""
echo "════════════════════════════════════════"
echo "  ✅ SETUP A16 COMPLETO"
echo "════════════════════════════════════════"
echo ""
echo "▶ Para lanzar supervisor:"
echo "  python3 ~/lbh-supervisor.py"
echo ""
echo "▶ Para ver métricas:"
echo "  python3 ~/lbh-metrics/lbh_metrics.py summary"
echo ""
echo "▶ Para registrar evento:"
echo "  python3 ~/lbh-metrics/lbh_metrics.py record PIPELINE_OK"
echo ""
echo "🐜 HormigasAIS · San Miguel, El Salvador · 2026"
