#!/usr/bin/env python3

import os
from datetime import datetime

print("\n🐜 H8 EJECUTORA ACTIVADA\n")

acciones = [
    "Comentar con pregunta abierta",
    "Responder comentarios existentes",
    "Compartir en grupo relevante",
    "Guardar desde cuenta secundaria",
    "Ver video completo 2 veces"
]

log_path = os.path.expanduser("~/hormigasais-lab/logs/h8_ejecuciones.log")

# ─────────────────────────────────────────────
# EJECUCIÓN AUTOMÁTICA (SIN BLOQUEO)
# ─────────────────────────────────────────────

print("📋 PLAN EJECUTADO:\n")

with open(log_path, "a") as f:
    f.write(f"\n[{datetime.now()}] H8 ejecutada\n")

    for i, accion in enumerate(acciones, 1):
        linea = f"{i}. {accion}"
        print(linea)
        f.write(f" - {accion}\n")

print("\n🧬 Registro guardado en:")
print(log_path)

print("\n🚀 H8 completada — ejecución no bloqueante\n")
