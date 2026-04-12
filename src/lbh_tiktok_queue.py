#!/usr/bin/env python3
"""
LBH-TikTok Queue v3.0 - INTELLIGENCE EDITION
Integra Transmuter y Persistencia de ADN
Autor: CLHQ | Protocolo: LBH v1.1
"""

import sqlite3
import time
import os
from datetime import datetime
# Importamos el transmutador polimórfico
import lbh_tiktok_transmuter as transmuter

BASE_DIR = os.path.expanduser("~/lbh-tiktok-adapter")
DB_PATH  = os.path.join(BASE_DIR, "tiktok_swarm.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # Tabla de señales (Cola de trabajo)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id    TEXT UNIQUE NOT NULL,
            tipo_evento INTEGER,
            lbh_hex     TEXT,
            prioridad   INTEGER DEFAULT 1,
            procesado   INTEGER DEFAULT 0,
            claimed_by  TEXT DEFAULT NULL,
            created_ts  INTEGER
        )
    """)
    # NUEVA: Tabla de Conocimiento (Persistencia de ADN)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conocimiento_colonia (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            adn_hash     TEXT,
            tipo         TEXT,
            intensidad   INTEGER,
            fecha_iso    TEXT,
            payload_hex  TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_conocimiento(datos_decodificados):
    """Persistencia de ADN: Guarda la feromona decodificada"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO conocimiento_colonia (adn_hash, tipo, intensidad, fecha_iso, payload_hex)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datos_decodificados['adn_hash'],
        datos_decodificados['tipo_evento'],
        datos_decodificados['intensidad_status'],
        datetime.fromtimestamp(datos_decodificados['fecha_unix']).isoformat(),
        datos_decodificados['checksum'] # Usamos el checksum como referencia de integridad
    ))
    conn.commit()
    conn.close()

def ingestar_feromona(asset_id, lbh_hex, tipo_evento=1, prioridad=1):
    ts = int(time.time())
    if tipo_evento == 2: prioridad = 10
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT OR REPLACE INTO signals (asset_id, tipo_evento, lbh_hex, prioridad, created_ts) VALUES (?, ?, ?, ?, ?)", 
                     (asset_id, tipo_evento, lbh_hex, prioridad, ts))
        conn.commit()
    except Exception as e: print(f"❌ Error en ingesta: {e}")
    finally: conn.close()

def reclamar_accion(worker_id="nodo-A16"):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT id, asset_id, lbh_hex, tipo_evento FROM signals WHERE procesado=0 AND claimed_by IS NULL ORDER BY prioridad DESC, created_ts ASC LIMIT 1").fetchone()
    if not row:
        conn.close()
        return None
    row_id, asset_id, lbh_hex, tipo_env = row
    conn.execute("UPDATE signals SET claimed_by=? WHERE id=?", (worker_id, row_id))
    conn.commit()
    conn.close()
    return {"id": row_id, "asset": asset_id, "hex": lbh_hex, "tipo": tipo_env}

if __name__ == "__main__":
    init_db()
    print("🐜 LBH-Swarm Intelligence Activa")

    # Ingestamos una señal de prueba de alta intensidad
    hex_viral = "0264d70edc002673e4ff69db08577008"
    ingestar_feromona("VIDEO-Tiktok-789", hex_viral, tipo_evento=2)

    accion = reclamar_accion("nodo-maestro")
    
    if accion:
        # INTEGRACIÓN TOTAL: Decodificación en tiempo real
        buffer_bin = bytes.fromhex(accion['hex'])
        datos = transmuter.decode_from_lbh(buffer_bin)
        
        if accion['tipo'] == 2:
            # 1. Reacción Física
            print("\n" + " " * 10 + "🐜 HormigasAIS")
            print("  .  .  .  .  . (Rastro de Feromona Digital)")
            print(f"  [ALTA INTENSIDAD: {datos['adn_hash']}]")
            os.system("termux-tts-speak 'Signal Surge Detected. Saving DNA to Colony Knowledge.'")
            
            # 2. Persistencia: Guardar en la base de datos de conocimiento
            guardar_conocimiento(datos)
            print(f"  ✅ ADN Persistido en conocimiento_colonia")

            # 3. Registro en Log Maestro
            ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            os.system(f"echo '[INTEL] {ahora} - DNA:{datos['adn_hash']} Intensity:{datos['intensidad_status']}' >> ~/hormigasais-lab/logs/master.log")

            # Mostrar resumen decodificado
            print(f"\n📊 RESUMEN DE INTELIGENCIA:")
            print(f"   Hash: {datos['adn_hash']}")
            print(f"   Status: {datos['intensidad_status']} (MAX)")
            print(f"   Verificación: {datos['verificacion']}")
