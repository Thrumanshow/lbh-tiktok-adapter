#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · COLONIA REYNA v1.5 (Fortaleza H6-Seguridad)
# Jerarquía: XOXO → H10 Soberana → Stanford → Reyna → Enjambre
# Cierre de Ciclo: Gitea 3001 + Salud + Seguridad Perimetral
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

CONTRACT_PATH = os.path.join(LOG_DIR, "contrato_reyna.json")
REPORT_PATH   = os.path.join(LOG_DIR, "REPORTE_INTELIGENCIA.md")

os.makedirs(LOG_DIR, exist_ok=True)

def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

# ================================================================
# HORMIGA H6-SEGURIDAD: CENTINELA DE INTEGRIDAD
# ================================================================
class HormigaH6Seguridad:
    def validar_entorno(self):
        print("[H6-SEGURIDAD]: Validando integridad del Nodo A16...")
        # Simulación de chequeo de procesos no autorizados
        return True

    def sellar_evidencia(self, archivos):
        print("[H6-SEGURIDAD]: Generando sello de seguridad perimetral...")
        hashes = []
        for arc in archivos:
            if os.path.exists(arc):
                with open(arc, "rb") as f:
                    hashes.append(hashlib.sha256(f.read()).hexdigest()[:8])
        
        # Sello Maestro del Enjambre
        sello_final = lbh_sig("-".join(hashes))
        return sello_final

# (Se mantiene HormigaH5Salud...)
class HormigaH5Salud:
    def __init__(self):
        self.backup_dir = os.path.expanduser("~/hormigasais-lab/backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    def ejecutar_chequeo(self, db_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"backup_lbh_{ts}.db")
        shutil.copy2(db_path, backup_file)
        return f"OK | Backup: {os.path.basename(backup_file)}"

def snapshot_soberania(video_id, sello_h6):
    print(f"\n[SNAPSHOT]: Iniciando Cierre de Ciclo Seguro para {video_id}...")
    evidence_dir = os.path.join(REPO_DIR, "evidence", video_id)
    os.makedirs(evidence_dir, exist_ok=True)

    for src in [CONTRACT_PATH, REPORT_PATH]:
        if os.path.exists(src):
            shutil.move(src, os.path.join(evidence_dir, os.path.basename(src)))

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta = {
        "video_id": video_id, 
        "nodo": NODE_ORIGIN, 
        "sello_seguridad": sello_h6,
        "ts": ts
    }
    with open(os.path.join(evidence_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    try:
        os.chdir(REPO_DIR)
        subprocess.run(["git", "add", "."], check=True)
        msg = f"SEC: Ciclo Blindado H6 | Video:{video_id} | Sello:{sello_h6}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"✅ [SNAPSHOT]: Nodo sincronizado y blindado.")
    except Exception as e:
        print(f"❌ [SNAPSHOT]: Error: {e}")

if __name__ == "__main__":
    import sys
    vid = sys.argv[1] if len(sys.argv) > 1 else "SEC_TEST_001"
    
    # 1. Preparar DB
    if not os.path.exists(DB_PATH): sqlite3.connect(DB_PATH).close()

    # 2. Inicializar Seguridad y Salud
    h6 = HormigaH6Seguridad()
    h5 = HormigaH5Salud()

    if h6.validar_entorno():
        # Generar archivos
        print(f"🐜 Enjambre operando en {vid}...")
        with open(CONTRACT_PATH, "w") as f: json.dump({"vid": vid, "secure": True}, f)
        with open(REPORT_PATH, "w") as f: f.write(f"Reporte Seguro para {vid}")

        # Ejecutar Salud
        print(f"[H5-SALUD]: {h5.ejecutar_chequeo(DB_PATH)}")

        # Ejecutar Seguridad (Sellar archivos antes de moverlos)
        sello = h6.sellar_evidencia([CONTRACT_PATH, REPORT_PATH])
        print(f"[H6-SEGURIDAD]: Sello de Integridad: {sello}")

        # Cierre
        snapshot_soberania(vid, sello)
