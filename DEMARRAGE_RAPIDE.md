# 🚀 Démarrage Rapide - VM de Déploiement

## ✅ Installation terminée !

Les outils suivants ont été installés avec succès :

- ✅ **Azure CLI** : 2.81.0
- ✅ **Azure Functions Core Tools** : 4.0.6280  
- ✅ **Python** : 3.12.3
- ✅ **.NET SDK** : 8.0.416
- ✅ **Git** : 2.43.0
- ⚠️  **Power Platform CLI** : Installation manuelle requise (voir ci-dessous)

## 🎯 Utilisation Immédiate

### Option 1 : Avec le wrapper (recommandé)

```bash
# Déployer un client
./deploy.sh
```

Le wrapper `deploy.sh` configure automatiquement tous les chemins nécessaires.

### Option 2 : Script Python direct

```bash
# Recharger le shell d'abord
source ~/.bashrc

# Puis déployer
python3 deploy_client.py
```

## 📋 Workflow de Déploiement Client

```bash
# 1. Se connecter avec le compte client
az login

# 2. Vérifier la connexion
az account show

# 3. Lancer le déploiement
./deploy.sh
```

Le script vous guidera interactivement pour :
1. Entrer le nom du client
2. Choisir la région Azure
3. Configurer OneDrive (optionnel)
4. Confirmer le déploiement
5. Créer toutes les ressources automatiquement
6. Tester l'API
7. (Optionnel) Déployer la solution Power Apps

## ⚙️ Configuration Power Platform CLI (si nécessaire)

Si vous avez besoin de déployer la solution Power Apps, installez pac CLI :

### Méthode 1 : Via dotnet (recommandé)

```bash
# Recharger le shell
source ~/.bashrc

# Installer pac CLI
dotnet tool install --global Microsoft.PowerApps.CLI.Tool --version 1.30.0

# Vérifier
pac --version
```

### Méthode 2 : Téléchargement manuel

```bash
# Télécharger depuis Microsoft
cd /tmp
wget https://aka.ms/PowerAppsCLI -O powerapps-cli.zip
unzip powerapps-cli.zip -d ~/.local/pac
chmod +x ~/.local/pac/pac
ln -sf ~/.local/pac/pac ~/.local/bin/pac

# Vérifier
~/.local/bin/pac --version
```

## 🧪 Tester l'Installation

```bash
# Recharger le shell
source ~/.bashrc

# Vérifier tous les outils
echo "Azure CLI:      $(az --version | head -1)"
echo "Functions:      $(func --version)"
echo ".NET SDK:       $(dotnet --version)"
echo "Python:         $(python3 --version)"
echo "Git:            $(git --version)"
```

## 📁 Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `deploy.sh` | 🎯 **Script principal** - Utilisez celui-ci ! |
| `deploy_client.py` | Script Python de déploiement |
| `GUIDE_DEPLOIEMENT.md` | Guide complet détaillé |
| `README_DEPLOIEMENT_VM.md` | Documentation VM |
| `Solution/` | Solution Power Apps à déployer |

## 🎬 Exemple de Session

```bash
devpp@vm:~/projects/bot_trad$ az login
# ... connexion Azure ...

devpp@vm:~/projects/bot_trad$ ./deploy.sh

============================================
  DÉPLOIEMENT BOT TRADUCTEUR
============================================

Nom du client (ex: contoso, acme-corp): acme-corp

Régions disponibles:
  1. France Central (Recommandé)
  2. West Europe
  3. North Europe
  4. East US
  5. West US

Choisissez une région (1-5): 1

RÉSUMÉ DU DÉPLOIEMENT
  Client: acme-corp
  Région: francecentral
  Resource Group: rg-translation-acme-corp
  Storage Account: sttradacmecorp
  Translator: translator-acme-corp
  Function App: func-translation-acme-corp
  OneDrive: Désactivé

Confirmez-vous ces informations? (o/n): o

[1/7] Création du Resource Group... ✓
[2/7] Création du Storage Account... ✓
[3/7] Création du Translator... ✓
[4/7] Création de la Function App... ✓
[5/7] Configuration... ✓
[6/7] Déploiement du code... ✓
[7/7] Tests... ✓

DÉPLOIEMENT TERMINÉ !

URL de l'API: https://func-translation-acme-corp.azurewebsites.net
Clé API: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Fichier: deployment-acme-corp-20260108-143000.json
```

## 🔍 Vérifier un Déploiement

```bash
# Tester l'API
export FUNC_URL="https://func-translation-{client}.azurewebsites.net"
export FUNC_KEY="votre-cle-api"

# Health check
curl "$FUNC_URL/api/health?code=$FUNC_KEY"

# Liste des langues
curl "$FUNC_URL/api/languages?code=$FUNC_KEY"

# Formats supportés
curl "$FUNC_URL/api/formats?code=$FUNC_KEY"
```

## 🧹 Supprimer un Déploiement

```bash
# Supprimer toutes les ressources du client
az group delete --name rg-translation-{client} --yes

# Exemple
az group delete --name rg-translation-acme-corp --yes
```

## 📊 Ce qui est Créé pour Chaque Client

```
Azure Subscription (client)
└── Resource Group: rg-translation-{client}
    ├── Storage Account: sttrad{client}
    │   ├── Container: doc-to-trad
    │   └── Container: doc-trad
    ├── Cognitive Services: translator-{client}
    └── Function App: func-translation-{client}
        ├── /api/health
        ├── /api/start_translation
        ├── /api/check_status/{id}
        ├── /api/get_result/{id}
        ├── /api/languages
        └── /api/formats
```

## 💡 Astuces

### Se déconnecter après chaque client

```bash
# Important pour la sécurité
az logout
```

### Sauvegarder les infos de déploiement

Les fichiers `deployment-*.json` contiennent toutes les informations. **Conservez-les précieusement !**

### Vérifier les logs en temps réel

```bash
az functionapp log tail \
  --name func-translation-{client} \
  --resource-group rg-translation-{client}
```

### Lister tous les déploiements

```bash
# Lister tous les Resource Groups de traduction
az group list --query "[?starts_with(name, 'rg-translation-')].{Name:name, Location:location}" -o table
```

## 🆘 Problèmes Courants

### Erreur : "func: command not found"

**Solution :**
```bash
source ~/.bashrc
# OU
./deploy.sh  # Utiliser le wrapper
```

### Erreur : "You are not logged in"

**Solution :**
```bash
az login
az account show  # Vérifier
```

### Erreur : "Resource already exists"

**Solution :**
```bash
# Utiliser un nom différent OU supprimer l'existant
az group delete --name rg-translation-{client} --yes
```

## 📚 Documentation Complète

Pour plus de détails :
- Guide complet : `cat GUIDE_DEPLOIEMENT.md`
- Architecture : `cat README_DEPLOIEMENT_VM.md`
- Troubleshooting : Voir section dans `GUIDE_DEPLOIEMENT.md`

## ✅ Checklist Déploiement

- [ ] Connecté au compte client (`az login`)
- [ ] Compte vérifié (`az account show`)
- [ ] Informations client préparées (nom, région)
- [ ] Lancé `./deploy.sh`
- [ ] Suivi les instructions interactives
- [ ] Testé l'API (endpoint /health)
- [ ] Sauvegardé le fichier deployment-*.json
- [ ] Transmis les infos au client de manière sécurisée
- [ ] Déconnecté (`az logout`)

---

**Prêt à déployer ? Exécutez : `./deploy.sh`** 🚀
