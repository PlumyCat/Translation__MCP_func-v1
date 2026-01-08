# 🚀 Bot Traducteur - VM de Déploiement

## 📋 Vue d'ensemble

Cette VM est dédiée au **déploiement du service de traduction** chez les clients. Elle permet aux techniciens de se connecter avec les comptes clients et de déployer automatiquement toutes les ressources nécessaires.

## ✨ Avantages de cette approche

- ✅ **Sécurité** : Le tech se connecte directement avec le compte client (pas de stockage de credentials)
- ✅ **Simplicité** : Un seul script interactif pour tout déployer
- ✅ **Isolation** : VM dédiée, démarre uniquement quand nécessaire
- ✅ **Maintenance** : Tous les outils sont pré-installés et à jour

## 📦 Contenu du projet

```
bot_trad/
├── setup_vm.sh                      # Script d'installation de la VM (1 fois)
├── deploy_client.py                 # Script de déploiement client (interactif)
├── GUIDE_DEPLOIEMENT.md             # Guide complet pour les techniciens
├── requirements-deploy.txt          # Dépendances Python pour le déploiement
│
├── Solution/
│   └── BotCopilotTraducteur_*.zip   # Solution Power Apps à déployer
│
├── copilot-deployment-bot/          # (Archive) Bot Copilot de déploiement
│   └── backend/                     # Code du backend d'automatisation
│
└── [Azure Functions du service de traduction]
    ├── health/
    ├── start_translation/
    ├── check_status/
    ├── get_result/
    ├── languages/
    ├── formats/
    ├── shared/
    └── requirements.txt
```

## 🎯 Workflow de déploiement

### 1️⃣ PRÉPARATION VM (une seule fois)

Lors de la première utilisation de la VM :

```bash
# Installer tous les outils nécessaires
sudo bash setup_vm.sh

# Recharger le shell
source ~/.bashrc
```

Cela installe :
- ✅ Azure Functions Core Tools v4
- ✅ Power Platform CLI
- ✅ .NET SDK 8.0
- ✅ Dépendances Python
- ✅ Outils système

### 2️⃣ DÉPLOIEMENT CLIENT

Pour chaque nouveau client :

```bash
# 1. Se connecter avec le compte client
az login

# 2. Vérifier la connexion
az account show

# 3. Lancer le déploiement
python3 deploy_client.py
```

Le script vous guide interactivement :
1. ✓ Vérifie les prérequis
2. ✓ Collecte les infos client (nom, région)
3. ✓ Crée les ressources Azure
4. ✓ Déploie l'Azure Function
5. ✓ Configure les variables d'environnement
6. ✓ Teste le déploiement
7. ✓ (Optionnel) Déploie la solution Power Apps

### 3️⃣ RÉSULTAT

À la fin, vous obtenez :
- 🌐 **URL de l'API** : `https://func-translation-{client}.azurewebsites.net`
- 🔑 **Clé API** : Pour sécuriser les appels
- 📄 **Fichier JSON** : `deployment-{client}-{timestamp}.json` avec toutes les infos
- ✅ **Service opérationnel** : Prêt à traduire des documents

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **GUIDE_DEPLOIEMENT.md** | Guide complet étape par étape pour les techniciens |
| **README.md** | Documentation technique du service de traduction |
| **copilot-deployment-bot/README.md** | Archive - Bot Copilot d'automatisation |

## 🔧 Outils installés

Après `setup_vm.sh`, la VM dispose de :

| Outil | Version | Usage |
|-------|---------|-------|
| Azure CLI | 2.81+ | Gestion des ressources Azure |
| Azure Functions Core Tools | 4.x | Déploiement des Functions |
| Power Platform CLI | Latest | Déploiement solutions Power Apps |
| Python | 3.12+ | Scripts d'automatisation |
| Git | 2.43+ | Gestion de version |
| .NET SDK | 8.0 | Runtime pour pac CLI |

## 🎬 Démarrage rapide

**Pour les techniciens qui utilisent la VM pour la première fois :**

```bash
# 1. Préparer la VM
sudo bash setup_vm.sh
source ~/.bashrc

# 2. Tester l'installation
az --version
func --version
pac --version

# 3. Lire le guide
cat GUIDE_DEPLOIEMENT.md

# 4. Déployer votre premier client
az login  # Avec le compte client
python3 deploy_client.py
```

**C'est tout ! 🎉**

## 🧹 Nettoyage

Pour supprimer un déploiement client :

```bash
# Supprimer toutes les ressources du client
az group delete --name rg-translation-{client} --yes
```

## 🆘 Support

En cas de problème :

1. **Consulter** : `GUIDE_DEPLOIEMENT.md` section Troubleshooting
2. **Vérifier** : `az account show` (bon compte ?)
3. **Logs** : `az functionapp log tail --name func-translation-{client} --resource-group rg-translation-{client}`
4. **Réinstaller** : `sudo bash setup_vm.sh`

## 📝 Notes importantes

### Sécurité
- ❌ Ne JAMAIS stocker de credentials dans des fichiers
- ✅ Toujours se connecter avec `az login` pour chaque client
- ✅ Se déconnecter après chaque déploiement : `az logout`

### Bonnes pratiques
- 📋 Toujours sauvegarder le fichier `deployment-*.json`
- 📊 Tester l'API après chaque déploiement
- 📧 Envoyer les infos (URL + clé) au client de manière sécurisée
- 🗑️ Nettoyer les déploiements de test

### Coûts
- 💰 Azure Functions Consumption : ~5-20€/mois par client
- 💰 Storage Standard LRS : ~1-5€/mois
- 💰 Azure Translator S1 : ~10€/mois + usage
- 📊 **Total : ~15-40€/mois par client**

## 🔄 Mise à jour de la VM

Pour mettre à jour les outils :

```bash
# Mettre à jour les packages système
sudo apt update && sudo apt upgrade -y

# Réinstaller les outils
sudo bash setup_vm.sh

# Mettre à jour le projet
git pull
```

## 📊 Architecture déployée par client

```
Client Azure Subscription
    │
    └── Resource Group: rg-translation-{client}
           │
           ├── Storage Account: sttrad{client}
           │   ├── Container: doc-to-trad
           │   └── Container: doc-trad
           │
           ├── Cognitive Services: translator-{client}
           │   └── API Key + Endpoint
           │
           └── Function App: func-translation-{client}
               ├── App Service Plan (Consumption Y1)
               ├── Runtime: Python 3.9
               └── Functions:
                   ├── /api/health
                   ├── /api/start_translation
                   ├── /api/check_status/{id}
                   ├── /api/get_result/{id}
                   ├── /api/languages
                   └── /api/formats

Power Platform (Client Environment)
    │
    └── Solution: Bot Copilot Traducteur
        ├── Bot Copilot Studio
        ├── Custom Connector → Function App
        ├── Flows (Power Automate)
        └── Topics de conversation
```

## 🎯 Checklist avant déploiement

- [ ] VM préparée (`setup_vm.sh` exécuté)
- [ ] Outils vérifiés (az, func, pac)
- [ ] Connecté avec le compte client (`az login`)
- [ ] Informations client collectées
- [ ] Guide de déploiement lu

## 🎯 Checklist après déploiement

- [ ] API testée et fonctionnelle
- [ ] Fichier JSON sauvegardé
- [ ] Informations transmises au client
- [ ] Solution Power Apps déployée (si applicable)
- [ ] Déconnexion Azure (`az logout`)

---

**Version** : 1.0  
**Dernière mise à jour** : Janvier 2026  
**Type** : VM de déploiement
