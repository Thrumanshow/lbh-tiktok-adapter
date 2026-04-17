#!/bin/bash

cd ~/lbh-tiktok-adapter || exit 1

echo "🐜 Sincronizando LBH TikTok Adapter..."

# ─────────────────────────────────────────────
# SINCRONIZAR ESTADO REMOTO (ANTI-CONFLICTOS)
# ─────────────────────────────────────────────
git fetch origin >/dev/null 2>&1
git fetch github >/dev/null 2>&1

# ─────────────────────────────────────────────
# DETECTAR CAMBIOS REALES (ANTI-RUIDO AVANZADO)
# ─────────────────────────────────────────────
# Verificar si hay commits pendientes hacia origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse origin/main 2>/dev/null)
BASE=$(git merge-base @ origin/main 2>/dev/null)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "🧘 Sin cambios remotos — sync omitido"
    exit 0
fi

# ─────────────────────────────────────────────
# PUSH A GITEA (SIEMPRE)
# ─────────────────────────────────────────────
if git push origin main; then
    echo "✅ Gitea OK"
else
    echo "⚠️ Gitea WARN"
fi

# ─────────────────────────────────────────────
# DETECTAR ÚLTIMO COMMIT
# ─────────────────────────────────────────────
LAST_COMMIT=$(git log -1 --pretty=%B 2>/dev/null)

# ─────────────────────────────────────────────
# PUSH A GITHUB (SOLO HITOS)
# ─────────────────────────────────────────────
if echo "$LAST_COMMIT" | grep -q "HITO"; then
    echo "🌐 HITO detectado → sincronizando GitHub..."
    
    if git push github main; then
        echo "🌐 GitHub OK"
    else
        echo "⚠️ GitHub WARN"
    fi
else
    echo "⏭️ GitHub omitido (commit no relevante)"
fi

# ─────────────────────────────────────────────
# LOG FINAL
# ─────────────────────────────────────────────
echo "--- Últimos commits ---"
git log --oneline -3

echo "🧬 Sync finalizado"
