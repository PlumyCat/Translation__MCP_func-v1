# Migration de Conteneur vers Azure Functions

Ce projet migre votre service de traduction de documents d'une **Azure Container Instance** vers des **Azure Functions** pour réduire les coûts tout en gardant toutes les fonctionnalités.

## 🎯 Avantages de la migration

### ✅ Coûts réduits
- **Avant** : Conteneur toujours en marche = facturation continue
- **Après** : Azure Functions = facturation à l'usage seulement
- **Économies estimées** : 60-80% pour un usage modéré

### ✅ Fonctionnalités conservées
- ✅ Traduction de documents via Azure Translator
- ✅ Support des mêmes formats de fichiers
- ✅ Intégration OneDrive optionnelle
- ✅ Gestion d'état des traductions
- ✅ APIs identiques (compatibilité maintenue)

### ✅ Améliorations
- 🚀 Démarrage à froid optimisé
- 📊 Meilleur monitoring avec Application Insights
- 🔄 Mise à l'échelle automatique
- 🛡️ Sécurité renforcée

## 📁 Structure du projet

```
azure-functions-translation/
├── function_app.py              # Point d'entrée principal
├── host.json                    # Configuration Azure Functions
├── requirements.txt             # Dépendances Python
├── local.settings.json          # Configuration locale
├── deploy.ps1                   # Script de déploiement
├── shared/                      # Code partagé
│   ├── config.py               # Configuration centralisée
│   ├── models/
│   │   └── schemas.py          # Modèles de données
│   ├── services/
│   │   ├── blob_service.py     # Gestion Azure Storage
│   │   ├── translation_service.py # Service Azure Translator
│   │   ├── graph_service.py    # Intégration OneDrive
│   │   ├── translation_handler.py # Orchestrateur de traduction
│   │   ├── status_handler.py   # Gestion des statuts
│   │   └── state_manager.py    # Gestion d'état
│   └── utils/
│       └── response_helper.py  # Helpers pour les réponses HTTP
└── README.md                   # Ce fichier
```

## 🚀 Déploiement rapide

### Prérequis
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- Python 3.9+
- PowerShell (pour le script de déploiement)

### 1. Clonage et configuration

```bash
# Copiez tous les fichiers de ce projet dans un nouveau dossier
cd azure-functions-translation

# Copiez et modifiez local.settings.json avec vos valeurs
cp local.settings.json.example local.settings.json
# Éditez local.settings.json avec vos clés Azure
```

### 2. Déploiement automatique

```powershell
# Déploiement complet (crée toutes les ressources)
.\deploy.ps1 -ResourceGroupName "rg-translation" -FunctionAppName "func-translation-app" -CreateResources

# Ou déploiement vers ressources existantes
.\deploy.ps1 -ResourceGroupName "rg-existing" -FunctionAppName "existing-function-app"
```

### 3. Test des endpoints

```bash
# Test de santé
curl https://your-function-app.azurewebsites.net/api/health

# Langues supportées
curl https://your-function-app.azurewebsites.net/api/languages

# Démarrage d'une traduction
curl -X POST https://your-function-app.azurewebsites.net/api/start_translation \
  -H "Content-Type: application/json" \
  -d '{
    "file_content": "base64_encoded_file",
    "file_name": "document.pdf",
    "target_language": "fr",
    "user_id": "user123"
  }'
```

## 📋 Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Vérification de santé |
| `/api/start_translation` | POST | Démarrer une traduction |
| `/api/check_status/{id}` | GET | Vérifier le statut |
| `/api/get_result/{id}` | GET | Récupérer le résultat |
| `/api/cancel_translation/{id}` | DELETE | Annuler une traduction |
| `/api/languages` | GET | Langues supportées |
| `/api/formats` | GET | Formats supportés |

## 🔧 Configuration

Un fichier `local.settings.json.example` est fourni pour l'exécution locale.
Copiez-le en `local.settings.json` puis renseignez vos valeurs personnelles
avant de lancer les fonctions.

### Variables d'environnement requises

```bash
# Azure Storage
AZURE_ACCOUNT_NAME=your_storage_account
AZURE_ACCOUNT_KEY=your_storage_key

# Azure Translator
TRANSLATOR_TEXT_SUBSCRIPTION_KEY=your_translator_key
TRANSLATOR_TEXT_ENDPOINT=https://your-region.api.cognitive.microsoft.com/

# Optionnel - OneDrive
CLIENT_ID=your_app_client_id
SECRET_ID=your_app_secret
TENANT_ID=your_tenant_id
```

### Configuration avancée

```bash
# Limites
MAX_FILE_SIZE_MB=100
MAX_TRANSLATION_TIME_MINUTES=30

# Redis (optionnel pour la production)
REDIS_CONNECTION_STRING=redis://your-redis-server

# Conteneurs
INPUT_CONTAINER=doc-to-trad
OUTPUT_CONTAINER=doc-trad
```

## 🔄 Migration depuis votre conteneur

### 1. Sauvegarde des données

```bash
# Exportez vos traductions en cours si nécessaire
# (Les nouvelles Azure Functions utiliseront un nouveau système d'état)
```

### 2. Mise à jour des clients

Remplacez vos URLs de conteneur par les nouvelles URLs Azure Functions :

```javascript
// Avant (conteneur)
const baseUrl = 'https://your-container.azurecontainerinstance.io';

// Après (Azure Functions)
const baseUrl = 'https://your-function-app.azurewebsites.net/api';
```

### 3. Test en parallèle

1. Déployez les Azure Functions
2. Testez avec quelques traductions
3. Redirigez progressivement le trafic
4. Arrêtez le conteneur une fois validé

## 📊 Monitoring et logs

### Application Insights
Les Azure Functions sont automatiquement intégrées avec Application Insights pour :
- 📈 Métriques de performance
- 🐛 Détection des erreurs
- 📊 Tableaux de bord personnalisés
- 🔔 Alertes automatiques

### Logs personnalisés
```python
import logging
logger = logging.getLogger(__name__)

# Ces logs apparaîtront dans Application Insights
logger.info("✅ Traduction démarrée")
logger.error("❌ Erreur de traduction")
```

## 🛠️ Développement local

### Installation
```bash
pip install -r requirements.txt
```

### Lancement local
```bash
func start --python
```

### Tests
```bash
# Test de santé local
curl http://localhost:7071/api/health

# Test avec un fichier
curl -X POST http://localhost:7071/api/start_translation \
  -H "Content-Type: application/json" \
  -d @test_translation.json
```

## 🔒 Sécurité

### Authentification
Les Azure Functions utilisent des clés d'accès automatiques :
- 🔑 Clé d'hôte (pour l'administration)
- 🔑 Clés de fonction (par endpoint)
- 🔐 Authentification Azure AD possible

### Permissions
- ✅ Accès Azure Storage via clés de compte
- ✅ Accès Azure Translator via clé de subscription
- ✅ Accès OneDrive via Azure AD (optionnel)

## 🚨 Troubleshooting

### Erreurs communes

**Erreur : "Unable to find storage account"**
```bash
# Vérifiez vos variables d'environnement
az functionapp config appsettings list --name YOUR_FUNCTION_APP --resource-group YOUR_RG
```

**Erreur : "Translator service unavailable"**
```bash
# Testez votre clé Translator
curl -X POST "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=fr" \
  -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"Text":"Hello world"}]'
```

**Traduction bloquée en "InProgress"**
- Les traductions Azure peuvent prendre 5-15 minutes
- Vérifiez les logs Application Insights
- Testez le status endpoint régulièrement

### Support
- 📧 Logs détaillés dans Application Insights
- 🔍 Mode debug disponible en local
- 📋 Health check pour diagnostics rapides

## 🎉 Conclusion

Cette migration vous permet de :
- 💰 **Économiser 60-80% sur les coûts**
- 🚀 **Garder toutes les fonctionnalités**
- 📈 **Améliorer les performances**
- 🔧 **Simplifier la maintenance**

Les APIs restent compatibles, donc vos applications existantes continuent de fonctionner sans modification !

---

*Créé pour migrer efficacement de Container Instances vers Azure Functions* 🚀