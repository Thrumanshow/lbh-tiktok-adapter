#!/usr/bin/env python3
import sys, os, json
from datetime import datetime

def sellar_mision():
    if len(sys.argv) < 2:
        print("⚠️ H10: Falta ID del video")
        return

    video_id = sys.argv[1]
    # CORRECCIÓN: Ruta directa al archivo .json
    ruta_evidencia = os.path.expanduser(f"~/lbh-tiktok-adapter/evidence/{video_id}.json")
    libro_mayor = os.path.expanduser("~/lbh-tiktok-adapter/contabilidad_soberana.json")

    if not os.path.exists(ruta_evidencia):
        print(f"⚠️ H10: No hay evidencia para el video {video_id}")
        return

    with open(ruta_evidencia, 'r') as f:
        evidencia = json.load(f)

    # Cálculo de utilidad LBH
    metricas = evidencia.get("metricas", {})
    compras = metricas.get("purchases", 0)
    utilidad = compras * 0.1265 

    asiento = {
        "timestamp": str(datetime.now()),
        "video_id": video_id,
        "detalles": {
            "ingreso_bruto": compras * 1.0,
            "utilidad_neta": utilidad
        },
        "adn": evidencia.get("adn", "SIN_ADN")
    }

    with open(libro_mayor, 'a') as f:
        f.write(json.dumps(asiento) + "\n")

    print(f"✅ H10: Asiento contable sellado para {video_id}. Utilidad: ${utilidad:.4f}")

if __name__ == "__main__":
    sellar_mision()
