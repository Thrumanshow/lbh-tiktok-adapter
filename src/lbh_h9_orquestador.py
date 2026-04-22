#!/usr/bin/env python3
import os, sys, json, re, hashlib
from datetime import datetime

def extraer_video_id(url):
    match = re.search(r"video/(\d+)", url)
    if not match:
        match = re.search(r"com/(\w+)", url)
    return match.group(1) if match else "ID_DESCONOCIDO"

def ejecutar_mision():
    if len(sys.argv) < 2:
        print("⚠️ Error: No se recibió URL")
        return

    url = sys.argv[1]
    video_id = extraer_video_id(url)
    
    print(f"\n🚀 Misión para Video: {video_id}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # ENTRADA DINÁMICA (Aquí es donde servimos el agua limpia)
    try:
        metricas = {
            "views":     int(input("👁️  Vistas:    ") or 0),
            "likes":     int(input("❤️  Likes:     ") or 0),
            "comments":  int(input("💬  Comms:     ") or 0),
            "saves":     int(input("🔖  Saves:     ") or 0),
            "shares":    int(input("↗️  Shares:    ") or 0),
            "purchases": int(input("💰  Compras:   ") or 0)
        }
    except ValueError:
        print("❌ Error: Debes ingresar números enteros.")
        return

    # Cálculo de Score LBH
    score = (metricas["likes"] * 2) + (metricas["comments"] * 5) + (metricas["purchases"] * 50)
    
    # Generar ADN Determinístico
    adn_base = f"LBH-{video_id}-{score}-{datetime.now().strftime('%Y%m%d')}"
    adn_hex = hashlib.sha256(adn_base.encode()).hexdigest()[:16]

    # Guardar Evidencia para H10
    evidencia = {
        "video_id": video_id,
        "url": url,
        "score": score,
        "adn": adn_hex,
        "metricas": metricas,
        "timestamp": str(datetime.now())
    }
    
    path_evidencia = os.path.expanduser(f"~/lbh-tiktok-adapter/evidence/{video_id}.json")
    os.makedirs(os.path.dirname(path_evidencia), exist_ok=True)
    
    with open(path_evidencia, "w") as f:
        json.dump(evidencia, f, indent=4)

    print(f"\n✅ Misión Finalizada")
    print(f"🧬 ADN: {adn_hex}")
    print(f"📊 Score: {score}")

if __name__ == "__main__":
    ejecutar_mision()
