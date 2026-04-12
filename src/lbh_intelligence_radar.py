#!/usr/bin/env python3
"""
LBH-Intelligence Radar & Reporter v1.0
Analiza tendencias, detecta patrones de ADN y genera reportes Markdown.
Autor: CLHQ | Protocolo: LBH v1.1
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/lbh-tiktok-adapter/tiktok_swarm.db")
REPORT_PATH = os.path.expanduser("~/hormigasais-lab/logs/REPORTE_INTELIGENCIA.md")

def ejecutar_radar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Análisis de Intensidad (Última hora)
    hace_una_hora = (datetime.now() - timedelta(hours=1)).isoformat()
    cursor.execute("""
        SELECT COUNT(*), AVG(intensidad) 
        FROM conocimiento_colonia 
        WHERE fecha_iso > ? AND intensidad > 200
    """, (hace_una_hora,))
    conteo, promedio_int = cursor.fetchone()
    
    # 2. Detección de Patrones (ADN Repetido)
    cursor.execute("""
        SELECT adn_hash, COUNT(*) as repeticiones 
        FROM conocimiento_colonia 
        GROUP BY adn_hash 
        HAVING repeticiones > 1
        ORDER BY repeticiones DESC
    """)
    patrones = cursor.fetchall()
    
    conn.close()
    return conteo, promedio_int, patrones

def generar_reporte_md(conteo, promedio, patrones):
    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    reporte = f"""# 🐜 Reporte de Inteligencia HormigasAIS
**Nodo:** A16 - San Miguel, SV
**Fecha de Generación:** {ahora}
**Protocolo:** LBH v1.1 (Soberano)

---

## 📡 Resumen del Radar (Última Hora)
- **Impulsos de Alta Intensidad (>200):** {conteo if conteo else 0}
- **Promedio de Intensidad detectada:** {round(promedio, 2) if promedio else 0}

## 🧠 Detección de Patrones (ADN Reincidente)
"""
    if patrones:
        reporte += "| ADN Hash | Avistamientos | Estado |\n|---|---|---|\n"
        for p in patrones:
            reporte += f"| `{p[0]}` | {p[1]} | 🔥 REINCIDENTE |\n"
            # Alerta especial en terminal si hay patrones
            os.system(f"termux-tts-speak 'Pattern detected. DNA {p[0]} is showing recurrence.'")
    else:
        reporte += "_No se detectan patrones repetidos en este ciclo._\n"

    reporte += "\n\n--- \n*Reporte autogenerado por la infraestructura soberana de HormigasAIS.*"
    
    with open(REPORT_PATH, "w") as f:
        f.write(reporte)
    
    print(f"✅ Reporte generado en: {REPORT_PATH}")
    if conteo > 0:
        print(f"📡 Radar: {conteo} impulsos detectados. ¡Actividad alta!")

if __name__ == "__main__":
    print("📡 Activando Radar de Inteligencia LBH...")
    c, p, pat = ejecutar_radar()
    generar_reporte_md(c, p, pat)
