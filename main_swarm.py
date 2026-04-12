#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · LBH-TikTok Adapter v2.0
# Orquestador Swarm con metricas reales + colonia A16
# Autor: CLHQ · San Miguel, El Salvador · 2026
# RFC-LBH-0004 + RFC-LBH-0006
# ================================================================

import sys, os, json, time, sqlite3, hmac, hashlib, re
sys.path.insert(0, os.path.join(os.getcwd(), chr(115)+chr(114)+chr(99)))

from viral_swarm_protocol import ViralSwarm
from lbh_tiktok_queue import init_db, ingestar_feromona, reclamar_accion

# ── CONFIG ────────────────────────────────────────────────────
COLONY_DB   = os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db")
COLONY_DB2  = os.path.expanduser("~/hormigasais-lab/lbh-node-service/lbh_nodo.db")
SWARM_LOG   = os.path.expanduser("~/hormigasais-lab/logs/tiktok_swarm.log")
HMAC_KEY    = b"hormigasais-sovereign-2026"
NODE_ORIGIN = "A16-SanMiguel-SV"

os.makedirs(os.path.dirname(SWARM_LOG), exist_ok=True)

# ── METRICAS TIKTOK REALES ────────────────────────────────────
# Estructura basada en SDK interno de TikTok:
# Firebase Analytics: session_start, video_view, like, share, purchase
# okhttp: GET /api/item/detail/{video_id}
# room/sqlite: cache local de engagement

ENGAGEMENT_WEIGHTS = {
    # Basado en algoritmo TikTok conocido
    "views":    0.1,   # bajo peso — inflable facilmente
    "likes":    1.0,   # peso base
    "comments": 3.0,   # alta interaccion = viral signal
    "shares":   5.0,   # maximo peso — distribucion organica
    "saves":    4.0,   # intencion de compra
    "purchases": 10.0, # conversion directa
}

def calcular_score_viral(metricas):
    score = 0
    for key, val in metricas.items():
        peso = ENGAGEMENT_WEIGHTS.get(key, 1.0)
        score += val * peso
    # Normalizar a 1-999
    return min(999, max(1, int(score / 100)))

def extraer_video_id(input_str):
    # Patrones TikTok reales:
    # https://www.tiktok.com/@user/video/1234567890
    # https://vt.tiktok.com/ZSHaDefLy/
    # 1234567890 (ID directo)
    patrones = [
        r"tiktok\.com/@[^/]+/video/(\d+)",
        r"vm\.tiktok\.com/([A-Za-z0-9]+)",
        r"vt\.tiktok\.com/([A-Za-z0-9]+)",
        r"^(\d{10,20})$",
    ]
    for patron in patrones:
        m = re.search(patron, input_str)
        if m:
            return m.group(1)
    return input_str.split("/")[-1].split("?")[0] or input_str

def clasificar_contenido(video_id, score):
    # Clasificacion basada en estructura Firebase de TikTok
    if score >= 900:
        return "MEGAVIRAL", 3, "#FF0000"
    elif score >= 500:
        return "VIRAL", 2, "#FF6600"
    elif score >= 200:
        return "TRENDING", 1, "#FFAA00"
    elif score >= 50:
        return "GROWING", 0, "#00FF88"
    else:
        return "COLD", 0, "#888888"

def emitir_feromona_colonia(video_id, hex_signal, score, categoria):
    # Conectar con la colonia HormigasAIS real
    for db_path in [COLONY_DB, COLONY_DB2]:
        try:
            conn = sqlite3.connect(db_path)
            # Verificar si tiene tabla feromonas compatible
            tablas = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type=chr(116)+chr(97)+chr(98)+chr(108)+chr(101)"
            ).fetchall()]
            if "feromonas" in tablas:
                conn.execute(
                    "INSERT INTO feromonas (nodo, payload, firma, ts) VALUES (?,?,?,?)",
                    (f"TIKTOK-{categoria}", hex_signal,
                     hmac.new(HMAC_KEY, hex_signal.encode(), hashlib.sha256).hexdigest()[:16],
                     int(time.time()))
                )
                conn.commit()
                conn.close()
                return True, db_path
            conn.close()
        except Exception:
            continue
    return False, None

def log_swarm(evento):
    with open(SWARM_LOG, "a") as f:
        f.write(f"{int(time.time())}|{NODE_ORIGIN}|{evento}" + chr(10))

# ── MODO MANUAL (metricas conocidas) ─────────────────────────
def modo_manual(video_id, score):
    categoria, tipo_evento, color = clasificar_contenido(video_id, score)
    swarm = ViralSwarm()
    hex_signal = swarm.generate_viral_pheromone(video_id, score)

    print(f"" + chr(10) + "🧬 Generando ADN LBH: {hex_signal}")
    print(f"📊 Categoria: [{categoria}] | Score: {score}")

    ingestar_feromona(video_id, hex_signal, tipo_evento=tipo_evento)
    log_swarm(f"INGEST|{video_id}|{categoria}|{score}")
    print(f"✅ 🚀 {categoria} ingestada: {video_id} [Prio: {score//100}]")

    ok, db = emitir_feromona_colonia(video_id, hex_signal, score, categoria)
    if ok:
        print(f"🐜 Feromona emitida a colonia: {db.split(chr(47))[-1]}")
    else:
        print(f"📡 Señal emitida al bus local. Nodos en espera...")

    return hex_signal, tipo_evento, categoria

# ── MODO AVANZADO (metricas detalladas) ──────────────────────
def modo_avanzado(video_id):
    print("" + chr(10) + "📊 Modo avanzado — ingresa métricas reales del video:")
    metricas = {}
    campos = [
        ("views",    "👁️  Vistas totales"),
        ("likes",    "❤️  Likes"),
        ("comments", "💬 Comentarios"),
        ("shares",   "↗️  Compartidos"),
        ("saves",    "🔖 Guardados"),
        ("purchases","💰 Compras (0 si no aplica)"),
    ]
    for key, label in campos:
        try:
            val = int(input(f"  {label}: ") or "0")
            metricas[key] = val
        except ValueError:
            metricas[key] = 0

    score = calcular_score_viral(metricas)
    print(f"" + chr(10) + "🧮 Score calculado por algoritmo LBH: {score}/999")
    return score

# ── INTERFAZ PRINCIPAL ────────────────────────────────────────
def modo_interactivo():
    init_db()
    print("" + chr(10) + "═"*40)
    print("  🐜 HORMIGASAIS - INTERFAZ DE SOBERANÍA v2.0")
    print("  LBH-TikTok Adapter | RFC-LBH-0004 + 0006")
    print("═"*40)

    try:
        video_input = input("🔗 URL o ID del Video TikTok: ").strip()
        if not video_input:
            print("❌ Error: Se requiere un objetivo.")
            return

        video_id = extraer_video_id(video_input)
        print(f"🎯 Video ID: {video_id}")

        print("" + chr(10) + "📈 Modo de entrada:")
        print("  1) Score manual (1-999)")
        print("  2) Métricas detalladas (calcula score automático)")
        modo = input("Selecciona [1/2]: ").strip() or "1"

        if modo == "2":
            score = modo_avanzado(video_id)
        else:
            print("" + chr(10) + "📈 Niveles: 1-100 (Bajo) | 500 (Medio) | 999 (CRÍTICO)")
            score = int(input("⚡ Nivel de Tracción [1-999]: ") or "500")

        score = max(1, min(999, score))
        hex_signal, tipo_evento, categoria = modo_manual(video_id, score)

        print("" + chr(10) + "─"*40)
        input("⌨️  Presiona Enter para activar el primer Worker...")

        tarea = reclamar_accion(f"nodo-{NODE_ORIGIN}-worker-01")
        if tarea:
            tipos = {2: "VIRAL 🔥", 1: "TRENDING 📈", 0: "GROWING 🌱", 3: "MEGAVIRAL 🚀"}
            tipo_label = tipos.get(tarea.get("tipo", 0), "UNKNOWN")
            print(f"" + chr(10) + "✅ [TRABAJO RECLAMADO]")
            print(f"🎯 Objetivo:  {tarea.get(chr(97)+chr(115)+chr(115)+chr(101)+chr(116), video_id)}")
            print(f"🏷️  Categoria: {tipo_label}")
            print(f"📊 Score:     {score}/999")
            print(f"🧩 Payload:   {tarea.get(chr(104)+chr(101)+chr(120), hex_signal)}")
            print(f"🐜 Nodo:      {NODE_ORIGIN}")
            print(f"🔐 RFC:       RFC-LBH-0004 + RFC-LBH-0006")
            log_swarm(f"CLAIMED|{video_id}|{categoria}|worker-01")
        else:
            print("⚠️  No hay tareas disponibles en la cola.")

        print("─"*40)
        print("" + chr(10) + "📊 Resumen de sesion:")
        print(f"  Video:    {video_id}")
        print(f"  Score:    {score}/999")
        print(f"  Señal:    {hex_signal}")
        print(f"  Nodo:     {NODE_ORIGIN}")
        print(f"  Log:      {SWARM_LOG}")
        print("" + chr(10) + "🐜 HormigasAIS · San Miguel, El Salvador · 2026")

    except KeyboardInterrupt:
        print("" + chr(10) + "" + chr(10) + "👋 Operación cancelada.")
    except Exception as e:
        print(f"" + chr(10) + "❌ Error en el protocolo: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    modo_interactivo()
