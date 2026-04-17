#!/usr/bin/env python3
# ================================================================
# 🧬 HORMIGASAIS · H9 ORQUESTADOR SOBERANO v2.0
# Cerebro Autónomo del Enjambre · Nodo A16
# ================================================================

import os, subprocess, requests, re, sys

NODE = "A16-SanMiguel-SV"

def expandir_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

def extraer_video_id(url):
    url = expandir_url(url)
    patrones = [r"video/(\d+)", r"(\d{10,20})"]
    for p in patrones:
        m = re.search(p, url)
        if m: return m.group(1)
    return url.split("/")[-1].split("?")[0]

def ejecutar_mision(url, metrics):
    video_id = extraer_video_id(url)
    print(f"\n🐜 H9 ACTIVANDO MISIÓN PARA: {video_id}")

    script = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_misión_viral.py")

    # FLUJO DE ENTRADA AUTOMÁTICO PARA lbh_misión_viral.py
    # [URL] -> [Opción 2: Completa] -> [Métricas] -> [s: Confirmar]
    input_data = "\n".join([
        url,
        "2", 
        str(metrics["views"]),
        str(metrics["likes"]),
        str(metrics["comments"]),
        str(metrics["saves"]),
        str(metrics["shares"]),
        str(metrics["purchases"]),
        "s"
    ]) + "\n"

    try:
        subprocess.run(
            ["python3", script],
            input=input_data,
            text=True
        )
        print(f"✅ Misión {video_id} procesada por el Enjambre")
    except Exception as e:
        print(f"❌ Error H9: {e}")

def main():
    print("🧬 H9 ORQUESTADOR SOBERANO ONLINE")
    print(f"Nodo: {NODE}\n")

    if len(sys.argv) < 2:
        print("⚠️ Uso: python3 lbh_h9_orquestador.py <url>")
        return

    url = sys.argv[1]
    
    # Simulación de captura de métricas (Próximamente vía API/Scraper)
    metrics = {
        "views": 583, "likes": 27, "comments": 0,
        "saves": 0, "shares": 0, "purchases": 0
    }

    print(f"🔗 URL TikTok: {url}")
    print("\n📊 Métricas cargadas automáticamente:")
    for k, v in metrics.items(): print(f"  {k}: {v}")

    ejecutar_mision(url, metrics)

if __name__ == "__main__":
    main()
