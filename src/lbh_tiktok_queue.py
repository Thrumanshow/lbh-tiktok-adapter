#!/usr/bin/env python3
"""
LBH-TikTok Queue v2.0 - SWARM EDITION
Soporta órdenes de compra (0x01) e impulsos virales (0x02)
Autor: CLHQ | Protocolo: LBH v1.1
"""

import sqlite3
import time
import os

BASE_DIR = os.path.expanduser("~/lbh-tiktok-adapter")
DB_PATH  = os.path.join(BASE_DIR, "tiktok_swarm.db")

# ─────────────────────────────────────────
# INICIALIZAR DB (Añadimos tipo_evento)
# ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id    TEXT UNIQUE NOT NULL, -- OrderID o VideoID
            tipo_evento INTEGER,              -- 1: Venta, 2: Viral
            lbh_hex     TEXT,
            prioridad   INTEGER DEFAULT 1,    -- 10: URGENTE/VIRAL, 1: Normal
            procesado   INTEGER DEFAULT 0,
            claimed_by  TEXT DEFAULT NULL,
            created_ts  INTEGER
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# INGESTAR FEROMONA (Soporta Viral y Venta)
# ─────────────────────────────────────────
def ingestar_feromona(asset_id, lbh_hex, tipo_evento=1, prioridad=1):
    ts = int(time.time())
    # Si es evento viral (2), forzamos prioridad máxima
    if tipo_evento == 2:
        prioridad = 10
        
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            INSERT OR REPLACE INTO signals
            (asset_id, tipo_evento, lbh_hex, prioridad, created_ts)
            VALUES (?, ?, ?, ?, ?)
        """, (asset_id, tipo_evento, lbh_hex, prioridad, ts))
        conn.commit()
        msg = "🚀 IMPULSO VIRAL" if tipo_evento == 2 else "📦 ORDEN COMPRA"
        print(f"✅ {msg} ingestada: {asset_id} [Prio: {prioridad}]")
    except Exception as e:
        print(f"❌ Error en ingesta: {e}")
    finally:
        conn.close()

# ─────────────────────────────────────────
# RECLAMAR (Prioridad DESC para que el 10 gane)
# ─────────────────────────────────────────
def reclamar_accion(worker_id="nodo-A16"):
    conn = sqlite3.connect(DB_PATH)
    # Cambiamos a DESC en prioridad para que los impulsos virales salgan primero
    row = conn.execute("""
        SELECT id, asset_id, lbh_hex, tipo_evento
        FROM signals
        WHERE procesado=0 AND claimed_by IS NULL
        ORDER BY prioridad DESC, created_ts ASC
        LIMIT 1
    """).fetchone()

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
    print("🐜 LBH-Swarm Queue Activa")
    
    # Prueba de concepto: Una orden normal y un impulso viral repentino
    ingestar_feromona("ORD-999", "0101...", tipo_evento=1, prioridad=1)
    ingestar_feromona("VIDEO-Tiktok-789", "0102...", tipo_evento=2)
    
    print("\n⚙️ Reclamando siguiente acción...")
    accion = reclamar_accion("nodo-maestro")
    if accion:
        # El sistema debería devolver el VIDEO-Tiktok-789 primero por su prioridad 10
        tipo = "VIRAL" if accion['tipo'] == 2 else "VENTA"
        print(f"🔥 Acción Urgente Reclamada: {accion['asset']} [TIPO: {tipo}]")
