#!/bin/bash
#
# Deploie le backend du bot de deploiement sur Azure Functions
#
# Usage:
#   ./deploy-bot-backend.sh [resource-group] [location] [function-app-name]
#
# Arguments:
#   resource-group    Nom du Resource Group (default: rg-deployment-bot)
#   location          Region Azure (default: francecentral)
#   function-app-name Nom de l'application Functions (default: func-deployment-bot)

set -e

# Parametres
RESOURCE_GROUP="${1:-rg-deployment-bot}"
LOCATION="${2:-francecentral}"
FUNCTION_APP_NAME="${3:-func-deployment-bot}"
STORAGE_ACCOUNT_NAME="stdeploymentbot"

echo "=== Deploiement du Backend du Bot ==="
echo ""

# Verifier Azure CLI
echo "[1/6] Verification de Azure CLI..."
if ! command -v az &> /dev/null; then
    echo "Azure CLI n'est pas installe. Installez-le depuis https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo "Azure CLI OK"

# Verifier Azure Functions Core Tools
echo "[2/6] Verification de Azure Functions Core Tools..."
if ! command -v func &> /dev/null; then
    echo "Azure Functions Core Tools n'est pas installe."
    echo "Installez-le: npm install -g azure-functions-core-tools@4"
    exit 1
fi
echo "Azure Functions Core Tools OK"

# Verifier la connexion
echo "[3/6] Verification de la connexion Azure..."
ACCOUNT=$(az account show 2>/dev/null || true)
if [ -z "$ACCOUNT" ]; then
    echo "Vous n'etes pas connecte. Executez 'az login' d'abord."
    exit 1
fi
echo "Connecte: $(echo $ACCOUNT | jq -r '.user.name')"
echo "Subscription: $(echo $ACCOUNT | jq -r '.name')"

# Creer le Resource Group
echo "[4/6] Creation du Resource Group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
echo "Resource Group cree: $RESOURCE_GROUP"

# Creer le Storage Account
echo "[5/6] Creation du Storage Account..."
# Nettoyer le nom
CLEAN_STORAGE_NAME=$(echo "$STORAGE_ACCOUNT_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9' | cut -c1-24)

az storage account create \
    --name "$CLEAN_STORAGE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --output none
echo "Storage Account cree: $CLEAN_STORAGE_NAME"

# Creer la Function App
echo "[6/6] Creation et deploiement de la Function App..."
az functionapp create \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --storage-account "$CLEAN_STORAGE_NAME" \
    --consumption-plan-location "$LOCATION" \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --os-type Linux \
    --output none
echo "Function App creee: $FUNCTION_APP_NAME"

# Deployer le code
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PATH="$SCRIPT_DIR/../backend"

cd "$BACKEND_PATH"

# Creer l'environnement virtuel et installer les dependances
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --quiet

# Deployer
func azure functionapp publish "$FUNCTION_APP_NAME" --python

deactivate

echo ""
echo "=== Deploiement termine ==="
echo ""
echo "URL de l'API: https://$FUNCTION_APP_NAME.azurewebsites.net/api"
echo ""
echo "Pour obtenir la Function Key:"
echo "az functionapp keys list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "Endpoints disponibles:"
echo "  POST /api/validate-credentials"
echo "  POST /api/deploy"
echo "  POST /api/validate-deployment"
echo "  GET  /api/deployments"
echo "  GET  /api/deployments/{clientName}"
