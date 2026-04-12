#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · COLONIA REYNA v1.3.1 (Gitea 3001 & Identity Fix)
# Jerarquía: XOXO → H10 Soberana → Stanford → Reyna → Enjambre
# Cierre de Ciclo: Sincronización con Gitea Local :3001
# Autor: HormigasAIS-Colonia-Soberana (chrisquionez354@gmail.com)
# ================================================================

import sqlite3, os, time, hmac, hashlib, socket, json, threading, shutil, subprocess
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────
HMAC_KEY     = b"hormigasais-sovereign-2026"
NODE_ORIGIN  = "A16-SanMiguel-SV"
GITEA_URL    = "http://localhost:3001/HormigasAIS-Colonia-Soberana/lbh-tiktok-adapter"
REPO_DIR     = os.path.expanduser("~/lbh-tiktok-adapter")
LOG_DIR      = os.path.expanduser("~/hormigasais-lab/logs")

# Archivos de la operación (Temporales antes del Snapshot)
CONTRACT_PATH = os.path.join(LOG_DIR, "contrato_reyna.json")
REPORT_PATH   = os.path.join(LOG_DIR, "REPORTE_INTELIGENCIA.md")

os.makedirs(LOG_DIR, exist_ok=True)

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

# --- LÓGICA DE SNAPSHOT INTEGRADA AL REPO REAL ---
def snapshot_soberania(video_id):
    print(f"\n[SNAPSHOT]: Iniciando Cierre de Ciclo para {video_id}...")
    
    # Crear carpeta de evidencia dentro del repo para historial inmutable
    evidence_dir = os.path.join(REPO_DIR, "evidence", video_id)
    os.makedirs(evidence_dir, exist_ok=True)

    # Mover archivos de logs al repositorio (Purga local automática)
    archivos_movidos = []
    for src in [CONTRACT_PATH, REPORT_PATH]:
        if os.path.exists(src):
            dest_name = os.path.basename(src)
            shutil.move(src, os.path.join(evidence_dir, dest_name))
            archivos_movidos.append(dest_name)

    if not archivos_movidos:
        print("⚠️ [SNAPSHOT]: No hay archivos de inteligencia para respaldar.")
        return

    # Generar Meta-Data de Soberanía vinculada al autor
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta = {
        "video_id": video_id,
        "timestamp": ts,
        "nodo": NODE_ORIGIN,
        "emisor": "chrisquionez354@gmail.com",
        "firma_clhq": lbh_sig(f"{video_id}|{ts}"),
        "status": "VALIDATED_BY_REYNA"
    }
    
    with open(os.path.join(evidence_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # --- SINCRONIZACIÓN CON GITEA :3001 ---
    try:
        os.chdir(REPO_DIR)
        # Asegurar configuración de identidad en el hilo de ejecución
        subprocess.run(["git", "config", "user.name", "HormigasAIS-Colonia-Soberana"], check=True)
        subprocess.run(["git", "config", "user.email", "chrisquionez354@gmail.com"], check=True)
        
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"HITO: Contrato Reyna validado | Video:{video_id} | Nodo:{NODE_ORIGIN}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        print(f"📡 Propagando a Gitea Local (HormigasAIS-Colonia-Soberana)...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"✅ [SNAPSHOT]: Ciclo cerrado. Contrato disponible en Gitea.")
        
    except Exception as e:
        print(f"❌ [SNAPSHOT]: Error en sincronización Git: {e}")

if __name__ == "__main__":
    import sys
    # Simulación de entrada: ID de video
    vid = sys.argv[1] if len(sys.argv) > 1 else "ZSH4acBq7"
    
    # Simulación de generación de documentos por el enjambre
    print(f"🐜 Iniciando Enjambre Reyna para: {vid}")
    with open(CONTRACT_PATH, "w") as f: 
        json.dump({"contrato": "REYNA_v1.3", "status": "active", "vid": vid, "author": "CLHQ"}, f)
    with open(REPORT_PATH, "w") as f: 
        f.write(f"# Reporte de Inteligencia HormigasAIS\nVideo: {vid}\nNodo: {NODE_ORIGIN}\n")
    
    # EJECUTAR CIERRE Y RESPALDO
    snapshot_soberania(vid)
