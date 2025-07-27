# 🚀 Guide de Déploiement ULTRA SIMPLE

Ce guide vous explique comment déployer votre service de traduction Azure Functions en **3 étapes simples**.

## 📋 Prérequis (5 minutes max)

### 1. Installer Azure CLI
```bash
# Windows (PowerShell en tant qu'administrateur)
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Installer Azure Functions Core Tools
```bash
# Windows (PowerShell en tant qu'administrateur)
winget install Microsoft.Azure.FunctionsCoreTools

# macOS
brew tap azure/functions
brew install azure-functions-core-tools@4

# Linux
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### 3. Se connecter à Azure
```bash
az login
```

## 🎯 Déploiement en 3 Étapes

### Étape 1: Créer la Configuration (2 minutes)
```powershell
# Ouvrir PowerShell dans le dossier du projet
.\create-config.ps1
```

Le script va vous demander :
- ✅ **Nom du groupe de ressources** (ex: `rg-translation-demo`)
- ✅ **Nom de l'application Functions** (ex: `func-translate-1234`) 
- ✅ **Nom du compte de stockage** (ex: `sttranslate1234`)
- ✅ **Nom du service Translator** (ex: `translator-1234`)
- ✅ **Région Azure** (recommandé: `francecentral`)
- ❓ **OneDrive** (optionnel, tapez `n` pour ignorer)

### Étape 2: Vérifier la Configuration
Ouvrez le fichier `deploy-config.json` créé et vérifiez que tout est correct :

```json
{
  "resourceGroupName": "rg-translation-demo",
  "functionAppName": "func-translate-1234",
  "storageAccountName": "sttranslate1234",
  "translatorName": "translator-1234",
  "location": "francecentral"
}
```

### Étape 3: Déployer ! (5-10 minutes)
```powershell
.\deploy.ps1
```

**C'est tout !** 🎉 Le script va :
- ✅ Créer toutes les ressources Azure
- ✅ Configurer les variables d'environnement
- ✅ Déployer votre code
- ✅ Tester que tout fonctionne

## 📊 Résultat Attendu

À la fin, vous verrez :

```
🎉 DÉPLOIEMENT TERMINÉ!

📍 Groupe de ressources: rg-translation-demo
🏠 Application Functions: func-translate-1234
🌐 URL de base: https://func-translate-1234.azurewebsites.net
🔗 URL Health Check: https://func-translate-1234.azurewebsites.net/api/health

Endpoints disponibles:
  GET  /api/health - Vérification du service
  GET  /api/languages - Langues supportées
  GET  /api/formats - Formats supportés
  POST /api/start_translation - Démarrer une traduction
  GET  /api/check_status/{id} - Vérifier le statut
  POST /api/get_result - Récupérer le résultat

🚀 Votre service de traduction est maintenant déployé et prêt à l'emploi!
```

## 🧪 Tester Votre Déploiement

### Test Rapide avec curl
```bash
# Test du health check
curl https://VOTRE-APP.azurewebsites.net/api/health

# Test des langues supportées
curl https://VOTRE-APP.azurewebsites.net/api/languages
```

### Test Complet avec test.http
1. Ouvrez le fichier `test.http`
2. Changez la première ligne :
   ```
   @baseUrl = https://VOTRE-APP.azurewebsites.net
   ```
3. Utilisez VS Code avec l'extension "REST Client" pour tester tous les endpoints

## 💰 Coûts Estimés

| Service | Coût/Mois | Notes |
|---------|-----------|-------|
| Azure Functions | ~0€ | Plan consommation (très peu d'usage) |
| Stockage Azure | ~1-2€ | Dépend des fichiers stockés |
| Azure Translator | **GRATUIT** | F0: 2M caractères/mois inclus |
| **TOTAL** | **~1-2€/mois** | Pour un usage normal |

## 🔧 Dépannage

### Problème: "Le nom est déjà pris"
**Solution**: Changez les noms dans `deploy-config.json` en ajoutant des chiffres :
```json
{
  "functionAppName": "func-translate-9999",
  "storageAccountName": "sttranslate9999"
}
```

### Problème: "Quota dépassé"
**Solution**: Choisissez une autre région dans `deploy-config.json` :
```json
{
  "location": "westeurope"
}
```

### Problème: "Erreur de déploiement du code"
**Solution**: 
1. Vérifiez que vous êtes dans le bon dossier
2. Vérifiez que `requirements.txt` existe
3. Relancez : `.\deploy.ps1`

### Problème: "Health check échoue"
**Solution**: Attendez 2-3 minutes que l'application démarre, puis testez à nouveau.

## 🗑️ Supprimer le Déploiement

Si vous voulez tout supprimer :
```bash
az group delete --name VOTRE-GROUPE-RESSOURCES --yes --no-wait
```

## 📞 Support

En cas de problème :
1. Vérifiez que tous les prérequis sont installés
2. Assurez-vous d'être connecté à Azure : `az login`
3. Vérifiez que votre abonnement Azure est actif
4. Consultez les logs d'erreur dans PowerShell

---

## 🎯 Récapitulatif Ultra-Rapide

```powershell
# 1. Installer les outils (une seule fois)
winget install Microsoft.AzureCLI
winget install Microsoft.Azure.FunctionsCoreTools
az login

# 2. Dans le dossier du projet
.\create-config.ps1    # Créer la config
.\deploy.ps1           # Déployer

# 3. Tester
curl https://VOTRE-APP.azurewebsites.net/api/health
```

**C'est vraiment aussi simple que ça !** 🚀