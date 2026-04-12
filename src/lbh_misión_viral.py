#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · MISION VIRAL v1.0
# Métricas reales → Score LBH → Objetivos 7 días → Reyna Pipeline
# Autor: CLHQ · San Miguel, El Salvador · 2026
# ================================================================

import sqlite3, os, time, hmac, hashlib, json, re
from datetime import datetime, timedelta

# ── CONFIG ────────────────────────────────────────────────────
HMAC_KEY    = b"hormigasais-sovereign-2026"
NODE_ORIGIN = "A16-SanMiguel-SV"
LBH_VERSION = "1.1"

DB_TIKTOK   = os.path.expanduser("~/lbh-tiktok-adapter/tiktok_swarm.db")
DB_COLONY   = os.path.expanduser("~/hormigasais-core/db/lbh_nodo.db")
MISSION_LOG = os.path.expanduser("~/hormigasais-lab/logs/misiones_virales.log")
MISSION_DB  = os.path.expanduser("~/lbh-tiktok-adapter/misiones.db")
REPORT_PATH = os.path.expanduser("~/hormigasais-lab/logs/REPORTE_MISION.md")

for f in [MISSION_LOG, REPORT_PATH]:
    os.makedirs(os.path.dirname(f), exist_ok=True)

# ── PESOS DE ENGAGEMENT (algoritmo TikTok real) ───────────────
PESOS = {
    "views":     0.1,   # inflable — peso bajo
    "likes":     1.0,   # base
    "comments":  3.0,   # interaccion alta = viral signal
    "shares":    5.0,   # distribucion organica — maximo peso
    "saves":     4.0,   # intencion de compra/consumo
    "purchases": 10.0,  # conversion directa
}

# ── OBJETIVOS ORGANICOS 7 DIAS ────────────────────────────────
# Basado en curva de crecimiento organico de TikTok
# Ratio promedio de videos en fase de despegue (score < 500)
RATIOS_7DIAS = {
    "views":    5.0,   # x5 en 7 dias (conservador)
    "likes":    7.5,   # x7.5 — ratio engagement/view mejora
    "comments": 45.0,  # x45 — comentarios crecen rapido en viral
    "saves":    7.5,   # x7.5
    "shares":   float("inf"),  # 0 -> objetivo base 10
    "purchases": 3.0,
}

MIN_OBJETIVOS = {
    "views":    3000,
    "likes":    150,
    "comments": 45,
    "saves":    30,
    "shares":   10,
    "purchases": 0,
}

# ── CRYPTO ────────────────────────────────────────────────────
def lbh_sig(payload):
    return hmac.new(HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()[:16]

def extraer_video_id(url):
    patrones = [
        r"tiktok\.com/@[^/]+/video/(\d+)",
        r"vm\.tiktok\.com/([A-Za-z0-9]+)",
        r"vt\.tiktok\.com/([A-Za-z0-9]+)",
        r"^(\d{10,20})$",
    ]
    for p in patrones:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return url.rstrip("/").split("/")[-1].split("?")[0]

# ── SCORE REAL ────────────────────────────────────────────────
def calcular_score(metricas):
    score = 0
    for key, val in metricas.items():
        peso = PESOS.get(key, 1.0)
        score += val * peso
    return min(999, max(1, int(score / 5)))

def clasificar(score):
    if score >= 900: return "MEGAVIRAL", 3
    if score >= 500: return "VIRAL", 2
    if score >= 200: return "TRENDING", 1
    if score >= 50:  return "GROWING", 0
    return "COLD", 0

# ── OBJETIVOS 7 DIAS ─────────────────────────────────────────
def calcular_objetivos(metricas, score):
    objetivos = {}
    for campo, valor_actual in metricas.items():
        if campo not in RATIOS_7DIAS:
            continue
        ratio = RATIOS_7DIAS[campo]
        minimo = MIN_OBJETIVOS.get(campo, 0)
        if ratio == float("inf") or valor_actual == 0:
            objetivo = minimo
        else:
            objetivo = max(int(valor_actual * ratio), minimo)
        crecimiento = objetivo - valor_actual
        pct = int((crecimiento / valor_actual * 100)) if valor_actual > 0 else 999
        objetivos[campo] = {
            "actual":    valor_actual,
            "objetivo":  objetivo,
            "delta":     crecimiento,
            "pct":       pct,
            "prioridad": "ALTA" if pct > 200 else "MEDIA" if pct > 50 else "BAJA",
        }
    return objetivos

# ── ENCODE LBH ────────────────────────────────────────────────
def encode_mision_lbh(video_id, score, metricas, objetivos):
    ts  = int(time.time())
    payload = (f"MISION|{video_id}|score:{score}|"
               f"v:{metricas.get('views',0)}|"
               f"l:{metricas.get('likes',0)}|"
               f"c:{metricas.get('comments',0)}|"
               f"s:{metricas.get('shares',0)}|"
               f"g:{metricas.get('saves',0)}")
    sig = lbh_sig(payload)
    adn = hashlib.sha256(payload.encode()).hexdigest()[:32]
    return {
        "lbh_packet": f"0x02{adn}",
        "sig":        sig,
        "adn_hex":    adn,
        "ts":         ts,
        "payload":    payload,
    }

# ── DB MISIONES ───────────────────────────────────────────────
def init_misiones_db():
    conn = sqlite3.connect(MISSION_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id    TEXT,
            url         TEXT,
            score       INTEGER,
            categoria   TEXT,
            metricas_json   TEXT,
            objetivos_json  TEXT,
            lbh_hex     TEXT,
            sig         TEXT,
            nodo        TEXT,
            ts          INTEGER,
            estado      TEXT DEFAULT 'ACTIVA'
        )
    """)
    conn.commit()
    conn.close()

def guardar_mision(video_id, url, score, categoria, metricas, objetivos, lbh):
    conn = sqlite3.connect(MISSION_DB)
    conn.execute("""
        INSERT INTO misiones
        (video_id, url, score, categoria, metricas_json, objetivos_json, lbh_hex, sig, nodo, ts)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (video_id, url, score, categoria,
           json.dumps(metricas, ensure_ascii=False),
           json.dumps(objetivos, ensure_ascii=False),
           lbh["lbh_packet"], lbh["sig"],
           NODE_ORIGIN, int(time.time())))
    conn.commit()
    conn.close()

def emitir_a_colonia(video_id, lbh):
    for db in [DB_COLONY]:
        try:
            conn = sqlite3.connect(db)
            tablas = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "feromonas" in tablas:
                conn.execute(
                    "INSERT INTO feromonas (nodo, payload, firma, ts) VALUES (?,?,?,?)",
                    (f"TIKTOK-MISION", lbh["payload"][:80], lbh["sig"], int(time.time())))
                conn.commit()
                conn.close()
                return True
            conn.close()
        except Exception:
            pass
    return False

# ── REPORTE MARKDOWN ──────────────────────────────────────────
def generar_reporte(video_id, url, score, categoria, metricas, objetivos, lbh):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = f"""# Mision Viral HormigasAIS
**Video ID:** {video_id}
**URL:** {url}
**Fecha:** {ahora}
**Nodo:** {NODE_ORIGIN}
**Score LBH:** {score}/999
**Categoria:** {categoria}
**Firma:** {lbh['sig']}
**ADN LBH:** {lbh['adn_hex']}

---

## Metricas Actuales vs Objetivos 7 Dias

| Metrica | Actual | Objetivo | Delta | Crecimiento | Prioridad |
|---|---|---|---|---|---|
"""
    for campo, datos in objetivos.items():
        md += (f"| {campo:10} | {datos['actual']:>8,} | "
               f"{datos['objetivo']:>8,} | "
               f"+{datos['delta']:>7,} | "
               f"{datos['pct']:>5}% | "
               f"{datos['prioridad']} |" + chr(10))

    md += f"""
---

## Plan de Accion LBH (Hormiga Reyna)

### H1 - Descargadora
- Descargar y analizar video {video_id}
- URL: {url}

### H2 - Marketing
- Score {score}/999 → Estrategia: """

    if score >= 500:
        md += "BOOST MAXIMO — publicar en todos los canales"
    elif score >= 200:
        md += "AMPLIFICAR — programar 3 posts proximas 2h"
    else:
        md += "NURTURE — contenido de apoyo organico"

    md += f"""

- Hashtags sugeridos segun engagement ratio
- Objetivo comentarios: +{objetivos.get('comments',{}).get('delta',0):,} (mayor retorno/esfuerzo)

### H3 - Inversion
- ROI proyectado segun score {score}
- Campo prioritario: shares (peso 5.0 en algoritmo TikTok)

### H4 - LBH Bridge
- Packet: {lbh['lbh_packet']}
- Sig: {lbh['sig']}

---

*Reporte autogenerado por HormigasAIS · CLHQ · San Miguel SV 2026*
"""
    with open(REPORT_PATH, "w") as f:
        f.write(md)
    return md

# ── LOG ───────────────────────────────────────────────────────
def log(msg):
    with open(MISSION_LOG, "a") as f:
        f.write(f"{int(time.time())}|{NODE_ORIGIN}|{msg}" + chr(10))

# ── INTERFAZ ──────────────────────────────────────────────────
def modo_interactivo():
    print()
    print("═" * 55)
    print("  HORMIGASAIS · MISION VIRAL v1.0")
    print("  Métricas reales → LBH → Objetivos → Reyna")
    print(f"  Nodo: {NODE_ORIGIN} | LBH v{LBH_VERSION}")
    print("═" * 55)

    init_misiones_db()

    # ── INPUT URL ──────────────────────────────────────────────
    url = input("" + chr(10) + "🔗 URL del video TikTok: ").strip()
    if not url:
        print("❌ Se requiere URL"); return
    video_id = extraer_video_id(url)
    print(f"🎯 Video ID: {video_id}")

    # ── INPUT METRICAS REALES ──────────────────────────────────
    print("" + chr(10) + "📊 Ingresa las métricas ACTUALES del video:")
    campos = [
        ("views",    "👁️  Vistas totales"),
        ("likes",    "❤️  Likes"),
        ("comments", "💬 Comentarios"),
        ("saves",    "🔖 Guardados"),
        ("shares",   "↗️  Compartidos"),
        ("purchases","💰 Compras (0 si no aplica)"),
    ]
    metricas = {}
    for key, label in campos:
        try:
            val = int(input(f"  {label}: ").strip() or "0")
            metricas[key] = val
        except ValueError:
            metricas[key] = 0

    # ── CALCULAR SCORE ─────────────────────────────────────────
    score     = calcular_score(metricas)
    categoria, tipo_evento = clasificar(score)

    print("" + chr(10) + "-" * 45)
    print(f"🧮 Score LBH calculado: {score}/999")
    print(f"📊 Categoria: [{categoria}]")

    # ── CALCULAR OBJETIVOS 7 DIAS ──────────────────────────────
    objetivos = calcular_objetivos(metricas, score)

    print("" + chr(10) + "🎯 OBJETIVOS 7 DIAS:")
    print(f"  {'Campo':10} {'Actual':>8} → {'Objetivo':>8}  {'Δ':>8}  %")
    print("  " + "-" * 50)
    for campo, d in objetivos.items():
        if campo == "purchases" and d["actual"] == 0 and d["objetivo"] == 0:
            continue
        print(f"  {campo:10} {d['actual']:>8,} → {d['objetivo']:>8,}  "
              f"+{d['delta']:>7,}  {d['pct']}%")

    # ── ENCODE LBH ────────────────────────────────────────────
    lbh = encode_mision_lbh(video_id, score, metricas, objetivos)
    print("" + chr(10) + f"🧬 ADN LBH: {lbh['adn_hex']}")
    print(f"🔐 Firma:   {lbh['sig']}")

    # ── CONFIRMAR ANTES DE PIPELINE ───────────────────────────
    print("" + chr(10) + "-" * 45)
    confirmar = input("⌨️  ¿Activar Hormiga Reyna con estos datos? [s/N]: ").strip().lower()
    if confirmar != "s":
        print("❌ Mision cancelada."); return

    # ── GUARDAR MISION ─────────────────────────────────────────
    guardar_mision(video_id, url, score, categoria, metricas, objetivos, lbh)
    log(f"MISION_CREADA|{video_id}|score:{score}|{categoria}")
    print("✅ Mision registrada en DB local")

    # ── EMITIR A COLONIA ──────────────────────────────────────
    ok = emitir_a_colonia(video_id, lbh)
    if ok:
        print("🐜 Feromona emitida a colonia A16")
    else:
        print("📡 Bus local — feromona en cola")

    # ── PIPELINE REYNA ────────────────────────────────────────
    print("" + chr(10) + "🐜 Activando Hormiga Reyna...")
    reyna_script = os.path.expanduser(
        "~/lbh-tiktok-adapter/src/lbh_colonia_reyna.py")
    if os.path.exists(reyna_script):
        os.system(f"python3 {reyna_script} '{video_id}' {score} '{lbh['adn_hex']}'")
    else:
        print("⚠️  lbh_colonia_reyna.py no encontrado — pipeline parcial")

    # ── REPORTE ───────────────────────────────────────────────
    generar_reporte(video_id, url, score, categoria, metricas, objetivos, lbh)
    print("" + chr(10) + f"📄 Reporte: {REPORT_PATH}")
    log(f"REPORTE_GENERADO|{video_id}|{lbh['sig']}")

    # ── RESUMEN ───────────────────────────────────────────────
    print()
    print("═" * 55)
    print(f"  MISION ACTIVA: {video_id}")
    print(f"  Score:     {score}/999 [{categoria}]")
    print(f"  ADN LBH:   {lbh['adn_hex']}")
    print(f"  Firma:     {lbh['sig']}")
    print(f"  DB:        {MISSION_DB}")
    print(f"  Reporte:   {REPORT_PATH}")
    print(f"  Log:       {MISSION_LOG}")
    print("═" * 55)
    print()

def ver_misiones():
    try:
        conn = sqlite3.connect(MISSION_DB)
        rows = conn.execute(
            "SELECT video_id, score, categoria, ts, estado FROM misiones "
            "ORDER BY ts DESC LIMIT 10").fetchall()
        conn.close()
        if not rows:
            print("Sin misiones registradas"); return
        print("" + chr(10) + "MISIONES ACTIVAS:")
        print(f"  {'Video ID':20} {'Score':>6} {'Cat':12} {'Fecha':20} Estado")
        print("  " + "-" * 70)
        for r in rows:
            fecha = datetime.fromtimestamp(r[3]).strftime("%Y-%m-%d %H:%M")
            print(f"  {r[0]:20} {r[1]:>6} {r[2]:12} {fecha:20} {r[4]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "misiones":
        ver_misiones()
    else:
        modo_interactivo()
