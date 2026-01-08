#!/bin/bash
#
# Wrapper pour le script de déploiement
# Configure automatiquement le PATH avant de lancer deploy_client.py
#

# Configuration du PATH
export PATH="$HOME/.local/bin:$HOME/.dotnet:$HOME/.dotnet/tools:$PATH"
export DOTNET_ROOT="$HOME/.dotnet"

# Vérification rapide des outils
if ! command -v func &> /dev/null; then
    echo "❌ Azure Functions Core Tools non trouvé"
    echo "   Exécutez d'abord: source ~/.bashrc"
    exit 1
fi

if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI non trouvé"
    exit 1
fi

# Lancer le script Python
python3 "$(dirname "$0")/deploy_client.py" "$@"
