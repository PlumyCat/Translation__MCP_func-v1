# Guide de Déploiement - Bot Traducteur

## Vue d'ensemble

Ce guide explique comment utiliser la VM de déploiement pour installer le service de traduction chez un client.

## Prérequis

- Accès à la VM de déploiement
- Credentials du client (compte Azure avec droits Contributor)
- Credentials Power Platform du client (optionnel, pour déployer le bot)

## Installation de la VM (Une seule fois)

La première fois que vous utilisez la VM, installez les outils nécessaires :

```bash
# Se connecter à la VM
ssh user@vm-deployment

# Aller dans le projet
cd ~/projects/bot_trad

# Installer les outils (SUDO REQUIS)
sudo bash setup_vm.sh

# Recharger le shell
source ~/.bashrc

# Vérifier que tout est OK
az --version
func --version
pac --version
```

## Déploiement chez un Client

### Étape 1 : Se connecter avec le compte client

```bash
# Se connecter à Azure avec le compte du client
az login

# Vérifier la souscription active
az account show
```

**IMPORTANT :** Vous devez être connecté avec un compte qui a les droits **Contributor** sur la souscription Azure du client.

### Étape 2 : Lancer le script de déploiement

```bash
cd ~/projects/bot_trad
python3 deploy_client.py
```

Le script va vous guider interactivement à travers :

1. ✓ Vérification des prérequis
2. ✓ Vérification de la connexion Azure
3. ✓ Collecte des informations client
4. ✓ Création des ressources Azure
5. ✓ Déploiement de l'Azure Function
6. ✓ Tests de fonctionnement
7. ✓ (Optionnel) Déploiement de la solution Power Apps

### Étape 3 : Informations à collecter

Le script vous demandera :

| Information | Description | Exemple |
|------------|-------------|---------|
| **Nom du client** | Nom court, sans espaces | `contoso`, `acme-corp` |
| **Région Azure** | Région de déploiement | France Central (recommandé) |
| **OneDrive** | Activer l'intégration OneDrive ? | Oui/Non |

Si OneDrive est activé, vous aurez besoin de :
- Client ID de l'App Registration Azure AD
- Client Secret
- Tenant ID
- Nom du dossier OneDrive

### Étape 4 : Résultat du déploiement

À la fin, vous obtiendrez :

- ✓ **URL de l'API** : `https://func-translation-{client}.azurewebsites.net`
- ✓ **Clé API** : Pour accéder aux endpoints
- ✓ **Fichier JSON** : `deployment-{client}-{date}.json` avec toutes les infos
- ✓ **Resource Group** : `rg-translation-{client}`

**Conservez précieusement ces informations !**

## Déploiement de la Solution Power Apps

### Option 1 : Via le script de déploiement

Le script `deploy_client.py` propose de déployer la solution automatiquement.

### Option 2 : Déploiement manuel

Si vous préférez déployer manuellement :

#### A. Se connecter à Power Platform

```bash
# Authentification Power Platform CLI
pac auth create --tenant <TENANT_ID> --url <ENVIRONMENT_URL>

# Exemple:
pac auth create --tenant xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx --url https://contoso.crm4.dynamics.com
```

#### B. Importer la solution

```bash
# Import de la solution
pac solution import --path Solution/BotCopilotTraducteur_1_0_0_2.zip --async

# Vérifier le statut
pac solution list
```

#### C. Configuration du bot

1. Ouvrir Power Apps : https://make.powerapps.com
2. Sélectionner l'environnement du client
3. Aller dans **Solutions** > **Bot Copilot Traducteur**
4. Configurer le **Connecteur personnalisé** :
   - URL de base : `https://func-translation-{client}.azurewebsites.net`
   - Authentification : API Key
   - Header : `x-functions-key`
   - Valeur : La clé API obtenue lors du déploiement
5. Tester la connexion
6. Publier le bot dans Copilot Studio

## Tests après déploiement

### Test de l'API

```bash
# Test endpoint health
curl "https://func-translation-{client}.azurewebsites.net/api/health?code={FUNCTION_KEY}"

# Test liste des langues
curl "https://func-translation-{client}.azurewebsites.net/api/languages?code={FUNCTION_KEY}"

# Test formats supportés
curl "https://func-translation-{client}.azurewebsites.net/api/formats?code={FUNCTION_KEY}"
```

### Test d'une traduction

```bash
# Exemple de traduction
curl -X POST "https://func-translation-{client}.azurewebsites.net/api/start_translation?code={FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "file_content": "<BASE64_ENCODED_FILE>",
    "file_name": "test.txt",
    "target_language": "fr",
    "user_id": "test-user"
  }'
```

## Nettoyage / Suppression

Pour supprimer complètement un déploiement client :

```bash
# Supprimer le Resource Group (supprime toutes les ressources)
az group delete --name rg-translation-{client} --yes --no-wait

# Exemple:
az group delete --name rg-translation-contoso --yes --no-wait
```

## Troubleshooting

### Erreur : "Commande non trouvée" (az, func, pac)

**Solution :** Rechargez votre shell
```bash
source ~/.bashrc
```

Si ça ne fonctionne toujours pas, réinstallez les outils :
```bash
sudo bash setup_vm.sh
```

### Erreur : "You are not logged in"

**Solution :** Connectez-vous avec le bon compte
```bash
az logout
az login
```

### Erreur : "Resource already exists"

**Solution :** Un déploiement existe déjà pour ce client. Options :

1. Utiliser un nom différent
2. Supprimer le déploiement existant :
```bash
az group delete --name rg-translation-{client} --yes
```

### Erreur : "Insufficient permissions"

**Solution :** Le compte utilisé n'a pas les droits nécessaires. Vérifiez que :
- Le compte a le rôle **Contributor** sur la souscription
- Vous êtes connecté au bon tenant : `az account show`

### Erreur lors du déploiement du code

**Solution :** Vérifiez que vous êtes dans le bon répertoire :
```bash
cd ~/projects/bot_trad
ls host.json  # Ce fichier doit exister
```

### La Function App ne répond pas

**Solution :** Attendez quelques minutes après le déploiement. Les Functions Apps peuvent prendre 2-5 minutes pour démarrer.

```bash
# Vérifier les logs
az functionapp log tail --name func-translation-{client} --resource-group rg-translation-{client}
```

### Erreur Power Platform : "Dataverse not enabled"

**Solution :** L'environnement n'a pas Dataverse. Options :

1. Créer un nouvel environnement avec Dataverse via le Power Platform Admin Center
2. Utiliser un environnement existant qui a déjà Dataverse

## Architecture déployée

```
┌─────────────────────────────────────────────────────────────┐
│                    Resource Group                           │
│                rg-translation-{client}                      │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  Storage Account │      │ Azure Translator │           │
│  │  sttrad{client}  │      │ translator-{...} │           │
│  │                  │      │                  │           │
│  │  • doc-to-trad   │      │  • API Key       │           │
│  │  • doc-trad      │      │  • Endpoint      │           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │         Azure Function App              │               │
│  │     func-translation-{client}           │               │
│  │                                         │               │
│  │  Endpoints:                             │               │
│  │  • /api/health                          │               │
│  │  • /api/start_translation               │               │
│  │  • /api/check_status/{id}               │               │
│  │  • /api/get_result/{id}                 │               │
│  │  • /api/languages                       │               │
│  │  • /api/formats                         │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Appel API
                            ▼
              ┌───────────────────────────┐
              │   Power Platform          │
              │   Copilot Studio Bot      │
              │                           │
              │   Interface utilisateur   │
              └───────────────────────────┘
```

## Coûts estimés

Pour information, voici les coûts mensuels approximatifs par client :

| Ressource | SKU | Coût mensuel estimé |
|-----------|-----|---------------------|
| Azure Functions | Consumption (Y1) | ~5-20€ (selon usage) |
| Storage Account | Standard LRS | ~1-5€ |
| Azure Translator | S1 | ~10€ + usage |
| Power Platform | Par utilisateur | Variable selon licence |

**Total estimé : 15-40€/mois** (hors licences Power Platform)

## Support

Pour toute question ou problème :
1. Vérifier ce guide
2. Consulter les logs Azure : `az functionapp log tail`
3. Contacter l'équipe DevOps

## Checklist de déploiement

- [ ] VM préparée avec `setup_vm.sh`
- [ ] Connecté à Azure avec le compte client (`az login`)
- [ ] Informations client collectées (nom, région)
- [ ] Script `deploy_client.py` exécuté avec succès
- [ ] Tests API réussis (`/health`, `/languages`, `/formats`)
- [ ] Fichier JSON de déploiement sauvegardé
- [ ] Solution Power Apps importée
- [ ] Connecteur personnalisé configuré
- [ ] Bot publié dans Copilot Studio
- [ ] Client informé et formé
- [ ] Documentation transmise au client

---

**Version** : 1.0  
**Dernière mise à jour** : Janvier 2026  
**Auteur** : Équipe DevOps
