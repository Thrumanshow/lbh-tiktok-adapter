#!/bin/bash
# HORMIGASAIS - Protocolo de Activación de Nodo Edge
# Objetivo: Despliegue inmersivo sin dependencias previas

echo "🐜 [HORMIGASAIS] Iniciando secuencia de acoplamiento..."

# 1. Solicitar acceso al almacenamiento (Tu Idea 1)
echo "📂 Solicitando permisos de memoria interna..."
termux-setup-storage
sleep 2

# 2. Configuración de dependencias mínimas de sistema
echo "🛠️ Preparando terreno (Python, Git, SQLite)..."
pkg update -y && pkg upgrade -y
pkg install -y python git sqlite3 openssh

# 3. Identificación del Nodo
READ_NODE_NAME=$(hostname)
echo "📍 Identificando hardware: $READ_NODE_NAME"

# 4. Clonación desde el Lab de HormigasAIS (Gitea Local)
# IMPORTANTE: Reemplazar 'localhost' por la IP de tu servidor en la red local
SERVER_IP="192.168.1.XX" # <-- Aquí pondrás la IP de tu servidor Gitea
echo "🧬 Descargando código soberano desde $SERVER_IP..."

git clone http://$SERVER_IP:3001/HormigasAIS-Colonia-Soberana/lbh-tiktok-adapter.git ~/lbh-tiktok-adapter

# 5. Instalación de la Lógica LBH
cd ~/lbh-tiktok-adapter
python3 -c "from src.lbh_tiktok_queue import init_db; init_db()"

# 6. Alias para el operador
echo "alias swarm='python3 ~/lbh-tiktok-adapter/main_swarm.py'" >> ~/.bashrc
echo "alias stats='python3 ~/lbh-tiktok-adapter/stats_swarm.py'" >> ~/.bashrc

echo "✅ NODO SINCRONIZADO Y LISTO PARA EL ATAQUE VIRAL"
echo "Escribe 'source ~/.bashrc' y luego 'swarm' para empezar."
