import sqlite3
import os

# Ruta soberana al DB
DB_PATH = os.path.expanduser("~/lbh-tiktok-adapter/tiktok_swarm.db")

def auditoria():
    if not os.path.exists(DB_PATH):
        print("❌ Error: No se encuentra la base de datos 'tiktok_swarm.db'.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Conteo por tipo de evento
    viral = c.execute("SELECT COUNT(*) FROM signals WHERE tipo_evento=2").fetchone()[0]
    ventas = c.execute("SELECT COUNT(*) FROM signals WHERE tipo_evento=1").fetchone()[0]
    
    # Conteo de estados
    reclamados = c.execute("SELECT COUNT(*) FROM signals WHERE claimed_by IS NOT NULL").fetchone()[0]
    pendientes = c.execute("SELECT COUNT(*) FROM signals WHERE claimed_by IS NULL").fetchone()[0]
    
    # Detalle de trabajadores activos
    workers = c.execute("SELECT DISTINCT claimed_by FROM signals WHERE claimed_by IS NOT NULL").fetchall()

    print("\n📊 AUDITORÍA DE MEMORIA - NODO A16 (San Miguel)")
    print("═" * 45)
    print(f"🔥 Impulsos Virales (LBH-02): {viral}")
    print(f"📦 Órdenes de Venta (LBH-01): {ventas}")
    print("─" * 45)
    print(f"🔄 Señales Reclamadas      : {reclamados}")
    print(f"⏳ Señales en Espera        : {pendientes}")
    print("─" * 45)
    print(f"👷 Hormigas Activas en DB  :")
    for w in workers:
        print(f"   └─ {w[0]}")
    print("═" * 45)
    conn.close()

if __name__ == "__main__":
    auditoria()
