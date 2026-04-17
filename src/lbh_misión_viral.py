import sqlite3, os, time, hmac, hashlib, json, re
try:
    import requests as _req
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

def expandir_url_corta(url):
    if not _HAS_REQUESTS: return url
    if "tiktok.com" in url and ("vt." in url or "vm." in url):
        try:
            r = _req.head(url, allow_redirects=True, timeout=5)
            return r.url
        except: pass
    return url

def extraer_video_id(url):
    u = expandir_url_corta(url)
    m = re.search(r'(\d{10,20})', u)
    if m: return m.group(1)
    return u.rstrip("/").split("/")[-1].split("?")[0]

def calcular_score(v, l, c, s, sh, cp):
    # Algoritmo LBH v1.1
    puntos = (v * 0.01) + (l * 2) + (c * 5) + (s * 3) + (sh * 4) + (cp * 10)
    score = min(int(puntos), 999)
    cat = "COLD"
    if score > 100: cat = "WARM"
    if score > 500: cat = "HOT"
    if score > 800: cat = "VIRAL"
    return score, cat

def generar_adn(vid, score):
    seed = f"{vid}-{score}-{time.time()}"
    return hashlib.md5(seed.encode()).hexdigest()

def ejecutar():
    print("\n" + "═"*55)
    print("  HORMIGASAIS · MISION VIRAL v1.1")
    print("  Nodo: A16-SanMiguel-SV | Modo Maestro CLHQ")
    print("═"*55)

    url = input("\n🔗 URL del video TikTok: ")
    video_id = extraer_video_id(url)
    print(f"🎯 Video ID detectado: {video_id}")

    print("\n" + "━"*55)
    print("  SELECCIONE MODO DE OPERACIÓN:")
    print("  [1] Misión Rápida (Test 1/999)")
    print("  [2] Misión Completa (Cálculo de Métricas)")
    print("━"*55)
    opcion = input("🐜 Selección > ")

    if opcion == "1":
        score = 1
        categoria = "TEST"
        print("\n⚡ Modo Test Activado: Score fijado en 1/999")
    else:
        print("\n📊 Ingresa las métricas ACTUALES:")
        v = int(input("  👁️  Vistas: ") or 0)
        l = int(input("  ❤️  Likes: ") or 0)
        c = int(input("  💬 Comentarios: ") or 0)
        s = int(input("  🔖 Guardados: ") or 0)
        sh = int(input("  ↗️  Compartidos: ") or 0)
        cp = int(input("  💰 Compras: ") or 0)
        score, categoria = calcular_score(v, l, c, s, sh, cp)

    adn = generar_adn(video_id, score)
    firma = hmac.new(b"CLHQ", adn.encode(), hashlib.sha256).hexdigest()[:16]

    print(f"\n🧮 Score: {score}/999 | Categoría: [{categoria}]")
    print(f"🧬 ADN: {adn}")
    
    confirmar = input("\n⌨️  ¿Activar Hormiga Reyna? [s/N]: ").lower()
    if confirmar == 's':
        print("\n🐜 Activando Hormiga Reyna...")
        reyna_script = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_colonia_reyna.py")
        if os.path.exists(reyna_script):
            import subprocess
            subprocess.run(["python3", reyna_script, video_id, str(score), adn])
        else:
            print("❌ Error: lbh_colonia_reyna.py no encontrado")

if __name__ == "__main__":
    ejecutar()
