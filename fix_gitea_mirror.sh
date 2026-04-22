#!/bin/bash
# Configurar credenciales en el mirror de Gitea
# Uso: bash fix_gitea_mirror.sh TU_TOKEN_GITHUB

TOKEN=
if [ -z "" ]; then
    echo "Uso: bash fix_gitea_mirror.sh GHPAT_TOKEN"
    echo "Obtener en: https://github.com/settings/tokens"
    exit 1
fi

# Guardar token en git credential store
git config --global credential.helper store
echo "https://Thrumanshow:@github.com" > ~/.git-credentials
echo "OK token guardado en ~/.git-credentials"

# Verificar
git ls-remote https://github.com/HormigasAIS/lbh-node-service.git 2>&1 | head -2
