#!/usr/bin/env python3
"""
LBH-TikTok Transmuter
Convierte órdenes TikTok E-commerce → Feromonas LBH binarias
Arquitectura: JSON → Buffer 16 bytes → LBH Signal

Autor: Cristhiam Leonardo Hernández Quiñonez (CLHQ)
Protocolo: LBH v1.1
2026
"""

import struct
import hashlib
import time
import json
import os
import sys

LBH_PROTOCOL_VERSION = 0x01
LBH_BUFFER_SIZE      = 16

# ─────────────────────────────────────────
# CHECKSUM LBH
# ─────────────────────────────────────────
def calcular_checksum(buffer: bytes) -> int:
    """CRC-16 simple para integridad de feromona"""
    crc = 0xFFFF
    for byte in buffer[:14]:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

# ─────────────────────────────────────────
# TRANSMUTER PRINCIPAL
# ─────────────────────────────────────────
def transform_to_lbh(tiktok_order: dict) -> bytes:
    """
    TikTok Order JSON → Buffer LBH 16 bytes

    Layout del buffer:
    [0]     type        uint8   1 byte  → tipo de evento
    [1-8]   order_id    uint64  8 bytes → ID del pedido
    [9]     status      uint8   1 byte  → estado del pedido
    [10-13] timestamp   uint32  4 bytes → unix timestamp
    [14-15] checksum    uint16  2 bytes → integridad CRC-16
    """
    buffer = bytearray(LBH_BUFFER_SIZE)

    # [0] Event type
    event_type = tiktok_order.get("type", 1)
    struct.pack_into(">B", buffer, 0, event_type & 0xFF)

    # [1-8] Order ID → uint64
    order_id_str = tiktok_order.get("data", {}).get("order_id", "0")
    order_id = int(order_id_str) & 0xFFFFFFFFFFFFFFFF
    struct.pack_into(">Q", buffer, 1, order_id)

    # [9] Order status
    status = tiktok_order.get("data", {}).get("order_status", 0)
    struct.pack_into(">B", buffer, 9, status & 0xFF)

    # [10-13] Timestamp
    timestamp = tiktok_order.get("timestamp", int(time.time()))
    struct.pack_into(">I", buffer, 10, timestamp & 0xFFFFFFFF)

    # [14-15] Checksum CRC-16
    checksum = calcular_checksum(bytes(buffer))
    struct.pack_into(">H", buffer, 14, checksum)

    return bytes(buffer)

# ─────────────────────────────────────────
# DECODIFICAR FEROMONA → JSON
# ─────────────────────────────────────────
def decode_from_lbh(buffer: bytes) -> dict:
    """Feromona LBH binaria → dict legible"""
    if len(buffer) != LBH_BUFFER_SIZE:
        raise ValueError(f"Buffer inválido: {len(buffer)} bytes (esperado {LBH_BUFFER_SIZE})")

    event_type = struct.unpack_from(">B", buffer, 0)[0]
    order_id   = struct.unpack_from(">Q", buffer, 1)[0]
    status     = struct.unpack_from(">B", buffer, 9)[0]
    timestamp  = struct.unpack_from(">I", buffer, 10)[0]
    checksum   = struct.unpack_from(">H", buffer, 14)[0]

    # Verificar integridad
    expected = calcular_checksum(buffer)
    integridad = "✅ VÁLIDO" if expected == checksum else "❌ CORRUPTO"

    return {
        "lbh_version":  LBH_PROTOCOL_VERSION,
        "event_type":   event_type,
        "order_id":     str(order_id),
        "order_status": status,
        "timestamp":    timestamp,
        "checksum":     hex(checksum),
        "integridad":   integridad,
        "buffer_hex":   buffer.hex(),
        "buffer_size":  len(buffer)
    }

# ─────────────────────────────────────────
# FEROMONA → LBH SIGNAL STRING
# ─────────────────────────────────────────
def to_lbh_signal(buffer: bytes, node="termux-A16") -> str:
    """Buffer binario → LBH://SIGNAL compatible con la red"""
    asset_hash = hashlib.sha256(buffer).hexdigest()
    ts = int(time.time())
    return f"""LBH://SIGNAL
version: 1.1
node: {node}
action: order_sync
asset: tiktok_order
hash: {asset_hash}
timestamp: {ts}
payload_hex: {buffer.hex()}
issued_by: CLHQ"""

# ─────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("🐜 LBH-TikTok Transmuter — demo")
    print("─" * 50)

    # Orden TikTok real
    tiktok_order = {
        "type": 1,
        "shop_id": "749123456789",
        "timestamp": 1710452491,
        "data": {
            "order_id": "5761234098123",
            "order_status": 100,
            "update_time": 1710452490
        }
    }

    print("📦 TikTok Order:")
    print(json.dumps(tiktok_order, indent=2))
    print()

    # Transmutación
    buffer = transform_to_lbh(tiktok_order)

    print(f"⚡ Feromona LBH ({len(buffer)} bytes):")
    print(f"   HEX: {buffer.hex()}")
    print(f"   BIN: {' '.join(f'{b:08b}' for b in buffer[:4])}...")
    print()

    # Decodificar
    decoded = decode_from_lbh(buffer)
    print("🔍 Decodificado:")
    for k, v in decoded.items():
        print(f"   {k:<15}: {v}")
    print()

    # LBH Signal
    signal = to_lbh_signal(buffer)
    print("📡 LBH://SIGNAL generado:")
    print(signal)
    print()

    # Eficiencia
    json_size = len(json.dumps(tiktok_order).encode())
    print(f"📊 Eficiencia de compresión:")
    print(f"   JSON original : {json_size} bytes")
    print(f"   Feromona LBH  : {len(buffer)} bytes")
    print(f"   Reducción     : {100 - (len(buffer)/json_size*100):.1f}%")
