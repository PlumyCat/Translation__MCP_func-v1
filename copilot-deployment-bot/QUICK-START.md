# Guide de Demarrage Rapide

## Pre-requis

1. **Azure CLI** installe et configure
2. **Azure Functions Core Tools** v4
3. **Python 3.9+**
4. **Licence Copilot Studio** (Power Platform)

## Installation en 3 etapes

### Etape 1: Deployer le Backend

```bash
# Cloner le repo
git clone <repo-url>
cd Translation__MCP_func-v1/copilot-deployment-bot

# Se connecter a Azure
az login

# Deployer le backend (Linux/Mac)
chmod +x scripts/deploy-bot-backend.sh
./scripts/deploy-bot-backend.sh

# OU pour Windows PowerShell
.\scripts\deploy-bot-backend.ps1
```

### Etape 2: Configurer le Custom Connector

1. Aller dans **Power Platform Admin Center**
2. Creer un nouveau **Custom Connector**
3. Importer `deployment-connector-swagger.json`
4. Dans l'onglet **Security**:
   - Type: API Key
   - Parameter name: `x-functions-key`
   - Parameter location: Header
5. Recuperer la Function Key:
   ```bash
   az functionapp keys list --name func-deployment-bot --resource-group rg-deployment-bot
   ```
6. Tester la connexion

### Etape 3: Creer le Bot dans Copilot Studio

1. Ouvrir **Copilot Studio**
2. Creer un nouveau bot: "Deployment Assistant"
3. Ajouter les topics depuis `topics/`
4. Configurer les actions avec le Custom Connector
5. Publier le bot

## Utilisation

Une fois le bot deploye, les techniciens peuvent simplement dire:

> "Je veux deployer pour un nouveau client"

Le bot va guider le technicien pour:
1. Entrer le nom du client
2. Choisir la region
3. Fournir les credentials Azure
4. Valider et lancer le deploiement

## Structure des fichiers

```
copilot-deployment-bot/
├── README.md                      # Documentation complete
├── QUICK-START.md                 # Ce guide
├── deployment-connector-swagger.json  # Definition OpenAPI du connector
├── topics/                        # Topics YAML pour Copilot Studio
│   ├── 01-start-deployment.yaml   # Topic principal de deploiement
│   ├── 02-check-status.yaml       # Verification de statut
│   ├── 03-validate-deployment.yaml # Validation
│   └── 04-list-deployments.yaml   # Liste des deploiements
├── backend/                       # Azure Functions backend
│   ├── requirements.txt
│   ├── host.json
│   ├── shared/                    # Modules partages
│   ├── validate_credentials/      # Validation des credentials
│   ├── deploy/                    # Deploiement complet
│   ├── validate_deployment/       # Validation post-deploiement
│   ├── list_deployments/          # Liste des deploiements
│   └── get_deployment_status/     # Statut d'un deploiement
└── scripts/                       # Scripts de deploiement
    ├── deploy-bot-backend.ps1     # Deploiement du backend (Windows)
    ├── deploy-bot-backend.sh      # Deploiement du backend (Linux/Mac)
    └── deploy-translation-service.ps1  # Deploiement manuel d'un client
```

## Credentials necessaires pour deployer un client

| Credential | Description | Ou le trouver |
|------------|-------------|---------------|
| Subscription ID | ID de l'abonnement Azure | Portal Azure > Subscriptions |
| Tenant ID | ID du tenant Azure AD | Portal Azure > Azure AD > Properties |
| Client ID | ID du Service Principal | Portal Azure > Azure AD > App registrations |
| Client Secret | Secret de l'application | Cree lors de la creation du SP |

### Creer un Service Principal

```bash
# Se connecter au tenant du client
az login --tenant <TENANT_ID>

# Creer le Service Principal
az ad sp create-for-rbac \
  --name "sp-translation-deployment" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

## Support

En cas de probleme:
1. Verifier les logs dans Application Insights
2. Tester les endpoints manuellement avec curl
3. Verifier les permissions du Service Principal
