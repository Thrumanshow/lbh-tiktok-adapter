#!/usr/bin/env python3
"""
LBH-TikTok Transmuter v2.2 - DECODE EDITION
Autor: Cristhiam Leonardo Hernández Quiñonez (CLHQ)
Protocolo: LBH v1.1 - 2026
"""

import struct
import hashlib
import time
import os

LBH_PROTOCOL_VERSION = 0x01
LBH_BUFFER_SIZE      = 16

def calcular_checksum(buffer: bytes) -> int:
    crc = 0xFFFF
    for byte in buffer[:14]:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def transform_to_lbh(tiktok_data: dict) -> bytes:
    buffer = bytearray(LBH_BUFFER_SIZE)
    event_type = tiktok_data.get("type", 1)
    struct.pack_into(">B", buffer, 0, event_type & 0xFF)

    if event_type == 2: # VIRAL
        video_id = str(tiktok_data.get("data", {}).get("video_id", "0"))
        id_hash = hashlib.sha256(video_id.encode()).digest()[:8]
        buffer[1:9] = id_hash
    else: # E-COMMERCE
        order_id_str = tiktok_data.get("data", {}).get("order_id", "0")
        order_id = int(order_id_str) & 0xFFFFFFFFFFFFFFFF
        struct.pack_into(">Q", buffer, 1, order_id)

    status = tiktok_data.get("data", {}).get("order_status", 0)
    struct.pack_into(">B", buffer, 9, status & 0xFF)
    timestamp = tiktok_data.get("timestamp", int(time.time()))
    struct.pack_into(">I", buffer, 10, timestamp & 0xFFFFFFFF)
    checksum = calcular_checksum(bytes(buffer))
    struct.pack_into(">H", buffer, 14, checksum)
    return bytes(buffer)

def decode_from_lbh(buffer: bytes) -> dict:
    """Feromona LBH binaria → dict legible"""
    event_type = struct.unpack_from(">B", buffer, 0)[0]
    id_polimorfico = buffer[1:9].hex()
    status = struct.unpack_from(">B", buffer, 9)[0]
    timestamp = struct.unpack_from(">I", buffer, 10)[0]
    checksum = struct.unpack_from(">H", buffer, 14)[0]

    expected = calcular_checksum(buffer)
    integridad = "✅ VÁLIDO" if expected == checksum else "❌ CORRUPTO"

    return {
        "tipo_evento": "VIRAL (2)" if event_type == 2 else "VENTA (1)",
        "adn_hash": id_polimorfico,
        "intensidad_status": status,
        "fecha_unix": timestamp,
        "checksum": hex(checksum),
        "verificacion": integridad
    }

if __name__ == "__main__":
    # El HEX generado anteriormente
    hex_feromona = "0264d70edc002673e4ff69db08577008"
    buffer_entrada = bytes.fromhex(hex_feromona)

    print("🐜 LBH-TikTok Transmuter — Decodificación de Soberanía")
    print("─" * 50)
    print(f"📥 Entrada HEX: {hex_feromona}")
    print("🔍 Procesando ADN binario...")
    print("─" * 50)

    try:
        resultado = decode_from_lbh(buffer_entrada)
        for clave, valor in resultado.items():
            print(f"   {clave:<20}: {valor}")
    except Exception as e:
        print(f"❌ Error en decodificación: {e}")
    
    print("─" * 50)
    print("✅ Operación completada: La feromona ha recuperado su significado.")
