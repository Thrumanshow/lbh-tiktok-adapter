#!/usr/bin/env python3
import os, time, json, sqlite3, socket, requests, subprocess
from threading import Thread 

# --- CONFIGURACIÓN SOBERANA ---
NODE_ID     = socket.gethostname()
BOT_TOKEN   = "8414322465:AAFgwr4ny4vN36rK3knCt3inJNzy-1xrVwU"
CHAT_ID     = "8463843180"
BASE_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"
DB          = os.path.expanduser("~/reyna_v11.db")
LIBRO_MAYOR = os.path.expanduser("~/lbh-tiktok-adapter/contabilidad_soberana.json")
user_states = {} 

def send(msg):
    """Envío inmutable de feromonas informativas a Telegram"""
    try:
        requests.post(f"{BASE_URL}/sendMessage",
                     data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
                     timeout=10)
    except: pass 

def obtener_balance():
    """Lógica de la Hormiga H10: Auditoría de Riqueza de la Colonia"""
    if not os.path.exists(LIBRO_MAYOR):
        return "📉 *BALANCE:* No hay registros contables en el Libro Mayor aún."
    
    total_bruto = 0.0
    total_iva = 0.0
    total_neta = 0.0
    conteo = 0 

    try:
        with open(LIBRO_MAYOR, 'r') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                det = data["detalles"]
                total_bruto += det["ingreso_bruto"]
                total_iva   += det["iva_retenido"]
                total_neta  += det["utilidad_neta"]
                conteo += 1 

        return (f"💰 *BALANCE SOBERANO - NODO {NODE_ID}*\n\n"
                f"🐜 Operaciones: `{conteo}`\n"
                f"💵 Ingreso Bruto: `${total_bruto:.2f}`\n"
                f"🏦 IVA a Declarar (13%): `${total_iva:.2f}`\n\n"
                f"📈 *UTILIDAD NETA: ${total_neta:.2f}*")
    except Exception as e:
        return f"⚠️ Error al leer Libro Mayor: {str(e)}"

def handle(chat_id, text):
    """Cerebro de la Reyna: Procesamiento de Comandos y Misiones"""
    global user_states
    raw_text = text.strip()
    cmd = raw_text.lower() 

    # 🧬 PRIORIDAD SOBERANA H9 (Iniciador de Misión)
    if raw_text.startswith("/h9"):
        user_states.pop(chat_id, None)
        try:
            url = raw_text.split(" ")[1]
            h9_path = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h9_orquestador.py")
            subprocess.Popen(["python3", h9_path, url])
            send(f"🧬 *[H9-AUTÓNOMO]*\nNodo `{NODE_ID}` activado.\n🔗 URL: {url}\n\n_Procesando feromonas..._")
            return
        except Exception as e:
            send(f"⚠️ Error H9: {str(e)}")
            return 

    # 💼 COMANDOS H10 (Contabilidad y Auditoría)
    if cmd == "/balance":
        send(obtener_balance())
        return 

    if raw_text.startswith("/auditar"):
        try:
            video_id = raw_text.split(" ")[1]
            h10_path = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h10_contadora.py")
            # La Reyna ordena a la H10 sellar la misión y capturamos el resultado
            resultado = subprocess.check_output(["python3", h10_path, video_id]).decode()
            send(f"💼 *AUDITORÍA H10*\n{resultado.strip()}")
            return
        except Exception as e:
            send(f"⚠️ Error en Auditoría: Verifique si el VIDEO_ID existe en evidence/.")
            return

    # 👑 COMANDOS ESTÁNDAR
    if cmd == "/start":
        menu = (f"👑 *REYNA v12.5 ONLINE*\n"
                f"Infraestructura: `{NODE_ID}`\n"
                f"Estado: `Soberano`\n\n"
                f"🤖 *COMANDOS OPERATIVOS:*\n"
                f"1. `/h9 [URL]` - Iniciar Misión Viral\n"
                f"2. `/auditar [ID]` - Sellar Factura e Ingreso\n"
                f"3. `/balance` - Ver Estado Financiero\n"
                f"4. `/reporte` - Log de Operaciones")
        send(menu)
        return

    if cmd == "/reporte":
        send("📋 *REPORTE SOBERANO:*\nAccediendo a logs de misión...")
        # Lógica extendida de reportes aquí
        return

def listener():
    """Oído de la Reyna: Escucha activa de señales de Telegram"""
    offset = None
    print(f"📡 Reyna escuchando en Nodo {NODE_ID}...")
    while True:
        try:
            r = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 30}).json()
            if r.get("result"):
                for u in r["result"]:
                    offset = u["update_id"] + 1
                    if "message" in u and "text" in u["message"]:
                        handle(str(u["message"]["chat"]["id"]), u["message"]["text"])
        except Exception as e:
            print(f"⚠️ Error de conexión: {e}")
            time.sleep(5) 

if __name__ == "__main__":
    print(f"👑 REYNA v12.5 ONLINE - NODO {NODE_ID}")
    # Lanzamos el oído de la colonia en un hilo independiente
    Thread(target=listener).start()

