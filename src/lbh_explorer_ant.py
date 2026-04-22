#!/usr/bin/env python3
# © 2026 HormigasAIS - Nodo Escuela / San Miguel
# Protocolo: LBH-2025 | Arquitecto: Ing. Cristhiam Quiñonez (CLHQ)
# Función: Hormiga Exploradora (Inyectora de Feromonas Neutra - Zero Cache)

import sys
import os
import json
import subprocess
import time

# --- DETECCIÓN DINÁMICA DE ENTORNO ---
BASE_HOME = os.path.expanduser("~")
# Forzamos la ruta absoluta de Termux para evitar el error de detección
ADAPTER_PATH = "/data/data/com.termux/files/home/xoxo-lbh-adapter"
EVIDENCE_PATH = os.path.join(BASE_HOME, "lbh-tiktok-adapter", "evidence")

sys.path.append(ADAPTER_PATH)

try:
    from adapter.core import XOXOAdapter
    from adapter.json_lbh import json_to_lbh
except ImportError:
    # Intento de rescate por si la ruta de Termux varía
    ADAPTER_PATH = os.path.join(BASE_HOME, "xoxo-lbh-adapter")
    sys.path.append(ADAPTER_PATH)
    try:
        from adapter.core import XOXOAdapter
        from adapter.json_lbh import json_to_lbh
    except:
        print(f"❌ [ERROR SOBERANO] Nodo LBH no encontrado en: {ADAPTER_PATH}")
        sys.exit(1)

def procesar_mision(url_inyectada):
    """
    Motor Adaptativo con Purga de Memoria.
    """
    print(f"📡 [INYECTANDO RASTRO NEUTRO] -> {url_inyectada}")
    
    # 1. PURGA Y EXTRACCIÓN (Hormiga Base H9 con --no-cache-dir)
    # --rm-cache-dir: Borra la memoria previa antes de actuar.
    # --no-cache-dir: Evita que se guarde rastro de esta ejecución.
    try:
        proc = subprocess.run(
            ["yt-dlp", "--rm-cache-dir"], capture_output=True, text=True
        ) # Limpieza previa
        
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", "--no-cache-dir", url_inyectada],
            capture_output=True, text=True, check=True
        )
        raw_data = json.loads(proc.stdout)
    except Exception as e:
        print(f"⛔ XOXO: El rastro no pudo ser extraído. Error: {e}")
        return

    # 2. Construcción de Feromona (Identidad Única por Ejecución)
    video_id = raw_data.get("id", f"inf_{int(time.time())}")
    feromona = {
        "type": "FEROMONA_EMITIDA",
        "origin": "A16_Exploradora_Neutra",
        "video_id": video_id,
        "metricas": {
            "vistas": raw_data.get("view_count", 0),
            "likes": raw_data.get("like_count", 0),
            "timestamp_lbh": int(time.time()) # Marca de tiempo real
        }
    }

    # 3. Activación del Puente XOXO y Emisión
    try:
        # Robot ID dinámico para evitar colisiones en el broker
        adapter = XOXOAdapter(robot_id=f"H_EXP_{int(time.time()) % 10000}")
        lbh_frame = json_to_lbh(feromona)
        
        adapter.client.connect(adapter.broker, adapter.port, 5)
        adapter.client.publish(adapter.rpt_topic, lbh_frame)
        print(f"📡 [BUS XOXO] Pulso emitido. Sincronía: {feromona['metricas']['timestamp_lbh']}")
        adapter.client.disconnect()

        # 4. Sello Stanford (Evidencia Soberana)
        os.makedirs(EVIDENCE_PATH, exist_ok=True)
        file_path = os.path.join(EVIDENCE_PATH, f"{video_id}.json")
        
        evidencia = {
            "adn_lbh": lbh_frame[-16:],
            "firma_maestra": "CLHQ-2026",
            "status": "VALIDADO_STANFORD",
            "payload": feromona
        }

        with open(file_path, 'w') as f:
            json.dump(evidencia, f, indent=2)
        
        print(f"💎 [STANFORD] Misión {video_id} sellada. Métricas frescas.")

    except Exception as e:
        print(f"⚠️ Error en cadena LBH: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        procesar_mision(sys.argv[1])
    else:
        print("💡 HormigasAIS: Inyecte una URL.")

