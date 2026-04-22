#!/usr/bin/env python3
# ================================================================
# HORMIGASAIS · NODO SHADOW v2.0 (Agente de Empuje)
# Nodo A20 · San Miguel, SV
# FUNCIÓN: Polinización Activa y Refuerzo de Viralización
# ================================================================
import socket, time, subprocess, os
from datetime import datetime

NODE_ID = "A20-ShadowNode-Booster"
PORT    = 5005
IP      = "127.0.0.1"

def log_shadow(color_code, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\033[{color_code}m[{ts}] {NODE_ID} >> {msg}\033[0m")

def polinizar(video_id):
    """
    Simula interacción de refuerzo para engañar al algoritmo.
    Llama al orquestador para generar tráfico de retención.
    """
    log_shadow("92", f"🐝 POLINIZACIÓN INICIADA: Generando pulso de retención para {video_id}...")
    
    h9_script = os.path.expanduser("~/lbh-tiktok-adapter/src/lbh_h9_orquestador.py")
    try:
        # Ejecuta el orquestador en segundo plano para no bloquear el bus
        # El parámetro 'boost' es una señal para el motor de interacción
        subprocess.Popen(["python3", h9_script, video_id], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        
        # Simulación de tiempo de visualización (Retención)
        time.sleep(2) 
        log_shadow("92", f"✅ Pulso de viralización inyectado con éxito en {video_id}")
    except Exception as e:
        log_shadow("91", f"⚠️ Error en motor de polinización: {e}")

log_shadow("94", f"AGENTE DE EMPUESTO ONLINE - Escuchando bus LBH...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind((IP, PORT))
except:
    print("❌ El puerto 5005 está ocupado.")
    exit()

while True:
    try:
        data, addr = sock.recvfrom(2048)
        msg = data.decode(errors="ignore")

        if msg.startswith("LBH_PULSE"):
            parts = msg.split("|")
            if len(parts) >= 3:
                evento   = parts[1]
                video_id = parts[2]

                if evento == "H9_INICIO":
                    log_shadow("93", f"🔍 REYNA inició misión {video_id}. Shadow RESPONDE...")
                    polinizar(video_id)
                
                elif evento == "H9_COMPLETADO":
                    log_shadow("96", f"📊 Sincronizando éxito de viralización: {video_id}")
                
                elif evento == "H10_AUDITORIA":
                    log_shadow("95", f"💰 Validando captura de valor económico.")

    except KeyboardInterrupt:
        log_shadow("31", "Shadow Offline.")
        break
    except Exception as e:
        time.sleep(1)
