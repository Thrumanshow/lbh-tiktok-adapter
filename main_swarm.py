#!/usr/bin/env python3
"""
HORMIGASAIS - Orquestador Interactivo (Nodo A16)
Manual Trigger para el Enjambre Viral
"""
import sys
import os

# Asegurar que reconozca los módulos en src/
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from viral_swarm_protocol import ViralSwarm
from lbh_tiktok_queue import init_db, ingestar_feromona, reclamar_accion

def modo_interactivo():
    init_db()
    print("\n" + "═"*40)
    print("  🐜 HORMIGASAIS - INTERFAZ DE SOBERANÍA")
    print("═"*40)
    
    try:
        video_input = input("🔗 URL o ID del Video TikTok: ").strip()
        if not video_input:
            print("❌ Error: Se requiere un objetivo.")
            return

        # Extraer ID si es URL (opcional, por ahora usamos el string)
        video_id = video_input.split('/')[-1].split('?')[0]
        
        print("\n📈 Niveles de Tracción: 1-100 (Bajo) | 500 (Medio) | 999 (CRÍTICO)")
        score = int(input("⚡ Nivel de Tracción [1-999]: ") or "500")

        # 1. Generar Feromona LBH
        swarm = ViralSwarm()
        hex_signal = swarm.generate_viral_pheromone(video_id, score)
        
        print(f"\n🧬 Generando ADN LBH: {hex_signal}")

        # 2. Inyectar en la Cola (Evento 2 = Viral)
        ingestar_feromona(video_id, hex_signal, tipo_evento=2)
        
        print(f"📡 Señal emitida al bus local. Nodos en espera...")

        # 3. Confirmación de Reclamo (Simulación de la primera 'hormiga' activa)
        print("\n" + "─"*40)
        input("⌨️ Presiona Enter para activar el reclamo del primer Worker...")
        
        tarea = reclamar_accion("nodo-A16-worker-01")
        if tarea:
            tipo = "VIRAL 🔥" if tarea['tipo'] == 2 else "VENTA 📦"
            print(f"\n✅ [TRABAJO RECLAMADO]")
            print(f"🎯 Objetivo: {tarea['asset']}")
            print(f"🏷️  Tipo    : {tipo}")
            print(f"🧩 Payload : {tarea['hex']}")
            print("─"*40)

    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error en el protocolo: {e}")

if __name__ == "__main__":
    modo_interactivo()
