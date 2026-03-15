#!/usr/bin/env python3
"""
LBH-TikTok Queue
Cola de pedidos TikTok en tiempo real
SQLite + prioridad + control de concurrencia

Autor: Cristhiam Leonardo Hernández Quiñonez (CLHQ)
Protocolo: LBH v1.1
2026
"""

import sqlite3
import time
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lbh_tiktok_transmuter import transform_to_lbh, decode_from_lbh

BASE_DIR = os.path.expanduser("~/hormigasais-lab/lbh-tiktok-adapter")
DB_PATH  = os.path.join(BASE_DIR, "tiktok_orders.db")

# Estados del pedido TikTok
ORDER_STATUS = {
    100: "CREATED",
    111: "AWAITING_SHIPMENT",
    112: "AWAITING_COLLECTION",
    121: "IN_TRANSIT",
    122: "DELIVERED",
    130: "COMPLETED",
    140: "CANCELLED"
}

# ─────────────────────────────────────────
# INICIALIZAR DB
# ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT UNIQUE NOT NULL,
            shop_id     TEXT,
            status_code INTEGER,
            status_name TEXT,
            lbh_hex     TEXT,
            lbh_hash    TEXT,
            prioridad   INTEGER DEFAULT 1,
            procesado   INTEGER DEFAULT 0,
            claimed_by  TEXT DEFAULT NULL,
            created_ts  INTEGER,
            updated_ts  INTEGER
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# INGESTAR ORDEN TIKTOK
# ─────────────────────────────────────────
def ingestar_orden(tiktok_order: dict, prioridad: int = 1) -> str:
    """
    Recibe JSON de TikTok → transmuta a LBH → persiste en SQLite
    Retorna el order_id
    """
    order_id   = tiktok_order.get("data", {}).get("order_id", "")
    shop_id    = tiktok_order.get("shop_id", "")
    status_code = tiktok_order.get("data", {}).get("order_status", 0)
    status_name = ORDER_STATUS.get(status_code, "UNKNOWN")

    # Transmutación LBH
    lbh_buffer = transform_to_lbh(tiktok_order)
    lbh_hex    = lbh_buffer.hex()

    import hashlib
    lbh_hash = hashlib.sha256(lbh_buffer).hexdigest()

    ts = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            INSERT OR REPLACE INTO orders
            (order_id, shop_id, status_code, status_name,
             lbh_hex, lbh_hash, prioridad, created_ts, updated_ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, shop_id, status_code, status_name,
              lbh_hex, lbh_hash, prioridad, ts, ts))
        conn.commit()
        print(f"✅ Orden ingestada: {order_id} [{status_name}] → LBH:{lbh_hex[:8]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

    return order_id

# ─────────────────────────────────────────
# RECLAMAR SIGUIENTE ORDEN
# ─────────────────────────────────────────
def reclamar_orden(worker_id: str = "worker-01") -> dict:
    """Control de concurrencia — solo un worker procesa cada orden"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("""
        SELECT id, order_id, lbh_hex, status_name
        FROM orders
        WHERE procesado=0 AND claimed_by IS NULL
        ORDER BY prioridad ASC, created_ts ASC
        LIMIT 1
    """).fetchone()

    if not row:
        conn.close()
        return None

    row_id, order_id, lbh_hex, status_name = row
    conn.execute("""
        UPDATE orders SET claimed_by=?, updated_ts=?
        WHERE id=?
    """, (worker_id, int(time.time()), row_id))
    conn.commit()
    conn.close()

    print(f"🔄 Reclamada: {order_id} [{status_name}] por {worker_id}")
    return {
        "id": row_id,
        "order_id": order_id,
        "lbh_hex": lbh_hex,
        "status_name": status_name,
        "worker": worker_id
    }

# ─────────────────────────────────────────
# COMPLETAR ORDEN
# ─────────────────────────────────────────
def completar_orden(row_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE orders SET procesado=1, updated_ts=?
        WHERE id=?
    """, (int(time.time()), row_id))
    conn.commit()
    conn.close()
    print(f"✅ Completada: orden #{row_id}")

# ─────────────────────────────────────────
# ESTADÍSTICAS
# ─────────────────────────────────────────
def stats():
    conn = sqlite3.connect(DB_PATH)
    total     = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pendientes = conn.execute("SELECT COUNT(*) FROM orders WHERE procesado=0").fetchone()[0]
    procesadas = conn.execute("SELECT COUNT(*) FROM orders WHERE procesado=1").fetchone()[0]
    en_proceso = conn.execute("SELECT COUNT(*) FROM orders WHERE claimed_by IS NOT NULL AND procesado=0").fetchone()[0]

    por_status = conn.execute("""
        SELECT status_name, COUNT(*) FROM orders GROUP BY status_name
    """).fetchall()
    conn.close()

    print(f"\n📊 TikTok Order Queue — Stats")
    print("─" * 40)
    print(f"   Total      : {total}")
    print(f"   Pendientes : {pendientes}")
    print(f"   En proceso : {en_proceso}")
    print(f"   Procesadas : {procesadas}")
    print(f"\n   Por status:")
    for s, c in por_status:
        print(f"   {s:<20} {c}")

if __name__ == "__main__":
    init_db()
    print("🐜 LBH-TikTok Queue — demo")
    print("─" * 50)

    # Simular órdenes Live Shopping
    ordenes = [
        {"type": 1, "shop_id": "749123456789", "timestamp": 1710452491,
         "data": {"order_id": "5761234098001", "order_status": 100, "update_time": 1710452490}},
        {"type": 1, "shop_id": "749123456789", "timestamp": 1710452492,
         "data": {"order_id": "5761234098002", "order_status": 111, "update_time": 1710452491}},
        {"type": 1, "shop_id": "749123456789", "timestamp": 1710452493,
         "data": {"order_id": "5761234098003", "order_status": 122, "update_time": 1710452492}},
        {"type": 1, "shop_id": "749123456789", "timestamp": 1710452494,
         "data": {"order_id": "5761234098004", "order_status": 130, "update_time": 1710452493}},
        {"type": 2, "shop_id": "749123456789", "timestamp": 1710452495,
         "data": {"order_id": "5761234098005", "order_status": 140, "update_time": 1710452494}},
    ]

    print(f"\n📥 Ingestando {len(ordenes)} órdenes TikTok...")
    for o in ordenes:
        ingestar_orden(o)

    stats()

    print(f"\n⚙️  Procesando órdenes...")
    for i in range(3):
        orden = reclamar_orden(f"worker-0{i+1}")
        if orden:
            time.sleep(0.1)
            completar_orden(orden["id"])

    stats()
