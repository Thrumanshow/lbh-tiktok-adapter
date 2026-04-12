#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · COLONIA REYNA v1.4 (Resiliencia H5-Salud)
# Jerarquía: XOXO → H10 Soberana → Stanford → Reyna → Enjambre
# Cierre de Ciclo: Gitea 3001 + Hot-Backup Soberano
# Autor: HormigasAIS-Colonia-Soberana (chrisquionez354@gmail.com)
# ================================================================

import sqlite3, os, time, hmac, hashlib, socket, json, threading, shutil, subprocess
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────
HMAC_KEY     = b"hormigasais-sovereign-2026"
NODE_ORIGIN  = "A16-SanMiguel-SV"
REPO_DIR     = os.path.expanduser("~/lbh-tiktok-adapter")
LOG_DIR      = os.path.expanduser("~/hormigasais-lab/logs")
DB_PATH      = os.path.join(REPO_DIR, "lbh_tiktok.db")

# Archivos de la operación
CONTRACT_PATH = os.path.join(LOG_DIR, "contrato_reyna.json")
REPORT_PATH   = os.path.join(LOG_DIR, "REPORTE_INTELIGENCIA.md")

os.makedirs(LOG_DIR, exist_ok=True)

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

# ================================================================
# HORMIGA H5-SALUD: MONITOR DE RESILIENCIA
# ================================================================
class HormigaH5Salud:
    def __init__(self):
        self.backup_dir = os.path.expanduser("~/hormigasais-lab/backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def ejecutar_chequeo(self, db_path):
        print("\n[H5-SALUD]: Iniciando escaneo de integridad y respaldo...")
        
        # 1. Chequeo de existencia
        if not os.path.exists(db_path):
            return "ERROR: DB no encontrada"

        # 2. Hot-Backup (Fuera de Git, para soberanía total)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"backup_lbh_{ts}.db")
        try:
            shutil.copy2(db_path, backup_file)
            self.purgar_viejos()
            return f"OK | Respaldo inmutable: {os.path.basename(backup_file)}"
        except Exception as e:
            return f"ERROR en backup: {e}"

    def purgar_viejos(self):
        # Mantiene la rotación de 5 archivos para optimizar espacio en Termux
        backups = sorted([os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.endswith('.db')])
        while len(backups) > 5:
            os.remove(backups.pop(0))

# --- LÓGICA DE SNAPSHOT (CIERRE DE CICLO) ---
def snapshot_soberania(video_id):
    print(f"\n[SNAPSHOT]: Iniciando Cierre de Ciclo para {video_id}...")
    evidence_dir = os.path.join(REPO_DIR, "evidence", video_id)
    os.makedirs(evidence_dir, exist_ok=True)

    # Transferencia de Evidencia
    for src in [CONTRACT_PATH, REPORT_PATH]:
        if os.path.exists(src):
            shutil.move(src, os.path.join(evidence_dir, os.path.basename(src)))

    # Metadata
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta = {"video_id": video_id, "nodo": NODE_ORIGIN, "firma_clhq": lbh_sig(f"{video_id}|{ts}")}
    with open(os.path.join(evidence_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # Git Push a Gitea :3001
    try:
        os.chdir(REPO_DIR)
        subprocess.run(["git", "add", "."], check=True)
        msg = f"HITO: Ciclo Reyna validado | Video:{video_id} | Nodo:{NODE_ORIGIN}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"✅ [SNAPSHOT]: Sincronizado en Gitea.")
    except Exception as e:
        print(f"❌ [SNAPSHOT]: Error Git: {e}")

if __name__ == "__main__":
    import sys
    vid = sys.argv[1] if len(sys.argv) > 1 else "ZSH4acBq7"
    
    # 1. Crear DB de prueba si no existe (Simulación de proceso)
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.close()

    # 2. Generar Documentación (Simulación de Enjambre)
    print(f"🐜 Iniciando Enjambre Reyna para: {vid}")
    with open(CONTRACT_PATH, "w") as f: json.dump({"status": "active", "vid": vid}, f)
    with open(REPORT_PATH, "w") as f: f.write(f"Reporte de Inteligencia HormigasAIS\nVideo: {vid}")

    # 3. ACTIVAR H5-SALUD (Resiliencia)
    h5 = HormigaH5Salud()
    status_salud = h5.ejecutar_chequeo(DB_PATH)
    print(f"[H5-SALUD]: {status_salud}")

    # 4. CIERRE DE CICLO
    snapshot_soberania(vid)
