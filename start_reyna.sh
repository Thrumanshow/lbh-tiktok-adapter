#!/bin/bash
# HORMIGASAIS - REYNA BOOT SCRIPT
echo "[*] Iniciando Secuencia de Despegue: A16 Reyna"

# 1. Limpieza de seguridad
fuser -k 9100/tcp 2>/dev/null
sleep 1

# 2. Lanzamiento en segundo plano (nohup mantiene el proceso vivo)
cd ~/lbh-tiktok-adapter
nohup python3 -u src/lbh_tunnel_v2.py server 9100 8100 > logs/reyna_session.log 2>&1 &

echo "[+] Reyna operando en segundo plano (Puerto 9100)."
echo "[+] Log de sesión: logs/reyna_session.log"
