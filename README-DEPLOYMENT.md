# 🚀 Déploiement ULTRA SIMPLE - 3 Clics

Déployez votre service de traduction Azure Functions en moins de 10 minutes !

## ⚡ DÉPLOIEMENT EXPRESS

### Prérequis (1 fois seulement)
```bash
# Installer Azure CLI et Functions Tools
winget install Microsoft.AzureCLI
winget install Microsoft.Azure.FunctionsCoreTools

# Se connecter à Azure  
az login
```

### Déploiement en 2 commandes
```powershell
# 1. Créer la configuration (interactive)
.\create-config.ps1

# 2. Déployer automatiquement  
.\deploy.ps1
```

**C'est tout !** 🎉

## 📁 Fichiers de Déploiement

| Fichier | Description | Usage |
|---------|-------------|-------|
| **`create-config.ps1`** | ✨ **Assistant de configuration** | Créé votre fichier de config interactivement |
| **`deploy.ps1`** | 🚀 **Script de déploiement principal** | Déploie tout automatiquement |
| **`test-deployment.ps1`** | 🧪 **Tests post-déploiement** | Vérifie que tout fonctionne |
| `deploy-config-example.json` | 📋 Exemple de configuration | Référence pour la config manuelle |
| `DEPLOYMENT-GUIDE.md` | 📚 Guide détaillé | Instructions complètes |

## 🔥 Utilisation Recommandée

### Première fois (Déploiement)
```powershell
# Étape 1: Configuration
.\create-config.ps1
# ➜ Remplissez les informations demandées

# Étape 2: Déploiement  
.\deploy.ps1
# ➜ Attendez 5-10 minutes

# Étape 3: Test
.\test-deployment.ps1
# ➜ Vérifiez que tout fonctionne
```

### Redéploiement (Code modifié)
```powershell
# Si vous modifiez le code, redéployez juste le code :
func azure functionapp publish VOTRE-APP-NAME --python
```

### Mise à jour de configuration
```powershell
# Si vous changez la config :
.\deploy.ps1
# ➜ Le script détecte les ressources existantes et met à jour
```

## 💡 Conseils Pro

### ✅ Bonnes Pratiques
- **Noms uniques** : Utilisez des suffixes comme votre nom ou date
- **Région proche** : Choisissez `francecentral` pour la France
- **Test local d'abord** : Testez avec `func start --python` avant de déployer
- **Sauvegarde config** : Gardez votre `deploy-config.json` en sécurité

### ⚠️ Éviter les Erreurs
- **Ne pas** modifier les noms après déploiement
- **Ne pas** mettre d'espaces dans les noms de ressources  
- **Ne pas** oublier de se connecter à Azure (`az login`)
- **Ne pas** utiliser des caractères spéciaux dans les noms

## 🛠️ Dépannage Express

### "Le nom est déjà pris"
```powershell
# Modifiez dans deploy-config.json :
"functionAppName": "func-translate-NOUVEAUNOM"
```

### "Erreur de permissions"
```bash
# Vérifiez votre connexion Azure :
az account show
```

### "Déploiement échoue"
```powershell
# Relancez simplement :
.\deploy.ps1
```

### "Health check échoue"
```bash
# Attendez 2-3 minutes puis :
curl https://VOTRE-APP.azurewebsites.net/api/health
```

## 💰 Coût Prévisionnel

| Service | Gratuit | Payant |
|---------|---------|--------|
| **Azure Functions** | ✅ Plan consommation | ~0€ pour usage normal |
| **Translator** | ✅ F0: 2M caractères/mois | Largement suffisant |
| **Stockage** | ❌ ~1-2€/mois | Inévitable mais très peu |

**Total estimé : ~1-2€/mois** pour un usage normal

## 🗑️ Suppression Complète

```bash
# Supprimer toutes les ressources créées :
az group delete --name VOTRE-GROUPE-RESSOURCES --yes
```

## 📞 Support Rapide

1. **Erreur de script** ➜ Vérifiez que PowerShell est en mode Administrateur
2. **Erreur Azure** ➜ `az login` puis relancez
3. **Erreur de déploiement** ➜ Changez les noms dans `deploy-config.json`
4. **Service ne répond pas** ➜ Attendez 5 minutes que Azure démarre

## 🎯 Résumé Ultra-Court

```powershell
az login                    # Se connecter
.\create-config.ps1        # Configurer  
.\deploy.ps1               # Déployer
.\test-deployment.ps1      # Tester
```

**4 commandes = Service de traduction déployé !** 🚀

---

> 💡 **Astuce** : Gardez votre `deploy-config.json` et `deployment-info.json` - ils contiennent toutes les infos de votre déploiement !