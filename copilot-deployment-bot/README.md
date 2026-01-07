# Bot Copilot Studio - Deployment Assistant

Bot conversationnel pour automatiser le deploiement du service de traduction Azure Functions.

## Vue d'ensemble

Ce bot permet aux techniciens de deployer le service de traduction simplement en fournissant les credentials du client. Le bot gere automatiquement:

1. Creation du Resource Group
2. Creation du Storage Account avec les containers
3. Creation du service Azure Translator
4. Deploiement de l'Azure Functions App
5. Configuration des variables d'environnement
6. Validation du deploiement

## Prerequis

### Pour le technicien
- Acces a Copilot Studio
- Credentials Azure du client (voir section Credentials)

### Pour l'installation du bot
- Licence Power Platform (Copilot Studio)
- Azure subscription pour le backend des actions
- Custom Connector configure

## Credentials necessaires

Le technicien doit fournir les informations suivantes:

| Information | Description | Exemple |
|-------------|-------------|---------|
| Subscription ID | ID de l'abonnement Azure du client | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| Tenant ID | ID du tenant Azure AD | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| Client ID | ID de l'application Azure AD (Service Principal) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| Client Secret | Secret de l'application Azure AD | `xxxxxxxxxxxxxxxxxxxxx` |
| Nom du client | Nom court pour identifier le client (sans espaces) | `contoso` |
| Region Azure | Region de deploiement | `francecentral`, `westeurope` |

### Creation du Service Principal (si necessaire)

```bash
# Se connecter au tenant du client
az login --tenant <TENANT_ID>

# Creer le Service Principal avec les droits Contributor
az ad sp create-for-rbac \
  --name "sp-translation-deployment" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

## Architecture du Bot

```
+-------------------+     +---------------------+     +------------------+
|   Copilot Studio  | --> | Custom Connector    | --> | Backend API      |
|   (Bot UI)        |     | (Power Platform)    |     | (Azure Functions)|
+-------------------+     +---------------------+     +------------------+
                                                              |
                                                              v
                                                      +------------------+
                                                      | Azure Resources  |
                                                      | (Client Tenant)  |
                                                      +------------------+
```

## Topics du Bot

### 1. Demarrer un deploiement
- Declencheur: "deployer", "nouveau deploiement", "installer"
- Collecte les credentials
- Lance le processus de deploiement

### 2. Verifier le statut
- Declencheur: "statut", "progression", "etat"
- Affiche l'etat du deploiement en cours

### 3. Valider un deploiement
- Declencheur: "valider", "tester", "verifier"
- Execute les tests de sante sur un deploiement existant

### 4. Lister les deploiements
- Declencheur: "liste", "historique", "deploiements"
- Affiche les deploiements effectues

### 5. Deployer la solution Power Platform
- Declencheur: "deployer la solution", "importer la solution", "pac deploy"
- Verifie si Dataverse est active
- Active Dataverse si necessaire (cree un nouvel environnement)
- Importe la solution du bot chez le client

## Installation

### 1. Deployer le Backend API

```bash
cd copilot-deployment-bot/backend
func azure functionapp publish <FUNCTION_APP_NAME>
```

### 2. Configurer le Custom Connector

1. Aller dans Power Platform Admin Center
2. Creer un nouveau Custom Connector
3. Importer le fichier `deployment-connector-swagger.json`
4. Configurer l'authentification (API Key ou OAuth)
5. Tester la connexion

### 3. Importer le Bot dans Copilot Studio

1. Ouvrir Copilot Studio
2. Creer un nouveau bot ou importer depuis les fichiers YAML
3. Configurer les actions avec le Custom Connector
4. Publier le bot

## Actions disponibles

| Action | Description | Parametres |
|--------|-------------|------------|
| `ValidateCredentials` | Valide les credentials Azure | subscriptionId, tenantId, clientId, clientSecret |
| `CreateResourceGroup` | Cree le Resource Group | clientName, region, credentials |
| `CreateStorageAccount` | Cree le Storage Account | clientName, resourceGroup, credentials |
| `CreateTranslatorResource` | Cree le service Translator | clientName, resourceGroup, credentials |
| `DeployFunctions` | Deploie l'application Functions | clientName, resourceGroup, credentials |
| `ConfigureEnvironment` | Configure les variables d'env | functionAppName, settings, credentials |
| `ValidateDeployment` | Teste le deploiement | functionAppUrl |
| `GetDeploymentStatus` | Obtient le statut | deploymentId |

## Flux de conversation type

```
Tech: Je veux deployer pour un nouveau client

Bot: Parfait ! Je vais vous guider pour le deploiement.
     Quel est le nom du client ? (ex: contoso)

Tech: acme-corp

Bot: Dans quelle region Azure voulez-vous deployer ?
     - France Central (recommande)
     - West Europe
     - North Europe

Tech: France Central

Bot: Maintenant, j'ai besoin des credentials Azure du client.
     Pouvez-vous me fournir le Subscription ID ?

Tech: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Bot: Tenant ID ?

Tech: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Bot: Client ID du Service Principal ?

Tech: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Bot: Et enfin, le Client Secret ?

Tech: ****************************

Bot: Je valide les credentials...
     Les credentials sont valides.

     Recapitulatif du deploiement:
     - Client: acme-corp
     - Region: francecentral
     - Resource Group: rg-translation-acme-corp
     - Storage Account: sttranslationacmecorp
     - Function App: func-translation-acme-corp

     Voulez-vous lancer le deploiement ?

Tech: Oui

Bot: Deploiement en cours...
     [1/5] Creation du Resource Group... OK
     [2/5] Creation du Storage Account... OK
     [3/5] Creation du Translator... OK
     [4/5] Deploiement des Functions... OK
     [5/5] Configuration... OK

     Deploiement termine avec succes !

     URL de l'API: https://func-translation-acme-corp.azurewebsites.net
     Cle API: ****************************

     Voulez-vous que je teste le deploiement ?
```

## Securite

- Les credentials ne sont jamais stockes de maniere permanente
- Les secrets sont masques dans les logs
- Communication chiffree (HTTPS)
- Authentification requise pour le connector

## Troubleshooting

### Erreur "Invalid credentials"
- Verifier que le Service Principal a les droits Contributor
- Verifier que le Client Secret n'est pas expire

### Erreur "Subscription not found"
- Verifier l'ID de souscription
- Verifier que le Service Principal a acces a cette souscription

### Erreur "Resource already exists"
- Un deploiement existe deja pour ce client
- Utiliser un nom different ou supprimer les ressources existantes

### Erreur "Dataverse not enabled"
- L'environnement Power Platform n'a pas Dataverse active
- Utiliser le topic "deployer la solution" pour creer un nouvel environnement
- Ou activer manuellement via le Power Platform Admin Center

### Erreur "pac CLI not found"
- Installer Power Platform CLI: `dotnet tool install --global Microsoft.PowerApps.CLI.Tool`
- Ou telecharger depuis: https://aka.ms/PowerAppsCLI

## Deploiement de la Solution via pac CLI

### Pre-requis
1. Power Platform CLI installe (`pac --version`)
2. Service Principal avec les roles:
   - Power Platform Administrator
   - Dynamics 365 Administrator

### Deploiement manuel

```powershell
# Verifier/Activer Dataverse
.\scripts\check-dataverse.ps1 -EnvironmentId "env-name" -TenantId "xxx" ...

# Creer un environnement avec Dataverse
.\scripts\enable-dataverse.ps1 -EnvironmentName "Translation-Prod" -Region "france" ...

# Importer la solution
.\scripts\import-solution.ps1 -EnvironmentUrl "https://xxx.crm4.dynamics.com" ...
```

### Deploiement complet automatise

```powershell
# Deploie tout en une seule commande
.\scripts\deploy-solution.ps1 `
    -EnvironmentUrl "https://xxx.crm4.dynamics.com" `
    -TenantId "xxx" `
    -ClientId "xxx" `
    -ClientSecret $secret
```

### Ajouter votre solution

1. Exporter la solution depuis votre environnement de dev
2. Placer le fichier ZIP dans `solution/TranslationDeploymentBot.zip`
3. Le bot utilisera automatiquement cette solution

## Actions disponibles

| Action | Description |
|--------|-------------|
| `ValidateCredentials` | Valide les credentials Azure |
| `FullDeployment` | Deploie le service de traduction complet |
| `ValidateDeployment` | Teste un deploiement |
| `ListDeployments` | Liste l'historique |
| `CheckDataverse` | Verifie si Dataverse est active |
| `EnableDataverse` | Cree un environnement avec Dataverse |
| `ImportSolution` | Importe la solution Power Platform |

## Support

Pour toute question, contacter l'equipe DevOps.
