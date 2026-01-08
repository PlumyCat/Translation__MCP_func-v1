# 🔧 Bot Traducteur - Guide Technique de Déploiement

> **Documentation complète pour techniciens** - Déploiement en ~1h30

---

## 🎯 Vue d'Ensemble

Bot de traduction d'entreprise basé sur Azure + Power Platform, permettant de traduire des documents dans 100+ langues directement depuis Microsoft Teams.

**Composants :**
- Backend Azure (Function App + Translator + Storage)
- Solution Power Platform (Copilot Studio + Power Automate)
- Bot Microsoft Teams (publié organisation)

---

## 🚀 Démarrage Rapide

### Étape 1 : Lire la Documentation

📘 **Commencez ici :**
```
👉 START_HERE.md
```

Ce document contient :
- Vue d'ensemble en 1 page
- Liens vers tous les guides
- Checklist complète
- Démarrage rapide

### Étape 2 : Guide Complet

📖 **Pour une vision complète :**
```
👉 DEMARRAGE_COMPLET.md
```

Contenu :
- Architecture détaillée
- Les 4 phases de déploiement
- Coûts et fonctionnalités
- Troubleshooting

### Étape 3 : Navigation

📑 **Pour naviguer dans la documentation :**
```
👉 INDEX_DOCUMENTATION.md
```

Organisation par :
- Scénario d'utilisation
- Rôle (Admin Azure, Power Platform, M365)
- Problème spécifique

---

## 📚 Documentation par Phase

### Phase 1 : Déploiement Azure (~30 min)

**Guide :** `GUIDE_DEPLOIEMENT.md`  
**⚠️ Important :** Lire `LIMITATIONS_AZURE_TRANSLATOR.md` avant de commencer !

**Commande :**
```bash
./deploy.sh
```

**Ce qui est créé :**
- Resource Group
- Storage Account (doc-to-trad, doc-trad)
- Azure Translator (F0 gratuit ou S1 payant)
- App Service Plan (B1)
- Function App (Python 3.12)

**Coût : ~14-16€/mois avec F0 (gratuit) ou ~24-26€/mois avec S1**

---

### Phase 2 : Power Platform (~40 min)

**Guide :** `GUIDE_POWER_PLATFORM_COMPLET.md`

**URL :** https://copilotstudio.microsoft.com

**Étapes :**
1. Importer `Solution/BotCopilotTraducteur_1_0_0_4.zip`
2. Créer connexion Blob Storage
3. Configurer variables environnement
4. Tester le bot

---

### Phase 3 : Publication Teams (~20 min)

**Guides disponibles :**
- 📸 `GUIDE_VISUEL_PUBLICATION.md` - **Rapide avec images** (recommandé)
- 📱 `GUIDE_PUBLICATION_TEAMS.md` - Détaillé complet

**Étapes :**
1. Publier le bot (Copilot Studio)
2. Configurer canal Teams
3. Personnaliser (icône + descriptions)
4. Options disponibilité → Organisation
5. Approuver (Centre Admin M365)
6. Publier à l'organisation
7. Épingler (optionnel)

---

## 📋 Prérequis

### Comptes et Licences

- [x] Compte Azure avec droits de création de ressources
- [x] Tenant Microsoft 365
- [x] Licences Power Platform (Power Apps + Copilot Studio)
- [x] Compte administrateur M365 (pour publication Teams)

### Outils (VM de déploiement)

- [x] Azure CLI
- [x] Python 3.12+
- [x] Azure Functions Core Tools
- [x] .NET SDK 8.0
- [x] Git

**Script d'installation :** `setup_vm.sh`

---

## 🗂️ Structure du Projet

```
bot_trad/
│
├── 📘 START_HERE.md                    ⭐ POINT D'ENTRÉE
├── 📘 DEMARRAGE_COMPLET.md             ⭐ GUIDE COMPLET
├── 📑 INDEX_DOCUMENTATION.md           Navigation
│
├── 📗 Guides de Déploiement/
│   ├── GUIDE_DEPLOIEMENT.md            Azure Backend
│   ├── GUIDE_POWER_PLATFORM_COMPLET.md Power Platform
│   ├── GUIDE_VISUEL_PUBLICATION.md     Teams (rapide)
│   └── GUIDE_PUBLICATION_TEAMS.md      Teams (détaillé)
│
├── ⚠️ Guides Importants/
│   ├── LIMITATIONS_AZURE_TRANSLATOR.md ⚠️ À LIRE !
│   └── README_DEPLOIEMENT_VM.md        Architecture
│
├── 🛠️ Scripts/
│   ├── deploy.sh                       Déploiement Azure
│   ├── deploy_client.py                Script Python principal
│   ├── deploy_power_platform.py        Guide interactif
│   └── setup_vm.sh                     Configuration VM
│
├── 🎨 Ressources/
│   ├── images/                         Captures d'écran
│   └── Solution/                       Fichier .zip solution
│
└── 📂 clients/                         Rapports interventions
    └── {client}/
        └── RAPPORT_INTERVENTION.md
```

---

## ⚡ Commandes Rapides

### Déploiement

```bash
# Déployer Azure
./deploy.sh

# Guide Power Platform interactif
python3 deploy_power_platform.py
```

### Tests

```bash
# Test santé API
curl https://func-translation-{client}.azurewebsites.net/api/health

# Langues disponibles
curl https://func-translation-{client}.azurewebsites.net/api/languages

# Formats supportés
curl https://func-translation-{client}.azurewebsites.net/api/formats
```

### Logs

```bash
# Logs en temps réel
az functionapp log tail --name func-translation-{client} \
  --resource-group rg-translation-{client}

# Logs Power Automate
# → make.powerapps.com → Solutions → Flux → Historique
```

### Nettoyage

```bash
# Supprimer un déploiement test
az group delete --name rg-translation-{client} --yes
```

---

## 🎯 Parcours par Profil

### 👨‍💻 Administrateur Système / DevOps

**Responsabilité :** Backend Azure

**Documents :**
1. `GUIDE_DEPLOIEMENT.md`
2. `LIMITATIONS_AZURE_TRANSLATOR.md` ⚠️
3. `README_DEPLOIEMENT_VM.md`

**Actions :**
- Déployer ressources Azure
- Configurer Function App
- Gérer coûts et quotas
- Monitoring

---

### 👨‍💼 Administrateur Power Platform

**Responsabilité :** Solution Copilot Studio

**Documents :**
1. `GUIDE_POWER_PLATFORM_COMPLET.md`
2. `deploy_power_platform.py`

**Actions :**
- Importer solution
- Configurer connexions
- Gérer variables environnement
- Tester bot

---

### 👨‍💼 Administrateur Microsoft 365

**Responsabilité :** Publication Teams

**Documents :**
1. `GUIDE_VISUEL_PUBLICATION.md` (rapide)
2. `GUIDE_PUBLICATION_TEAMS.md` (détaillé)

**Actions :**
- Approuver bot dans Centre Admin
- Publier à l'organisation
- Configurer épinglage
- Gérer permissions

---

## ⚠️ Points Critiques

### 1. Azure Translator F0

**⚠️ LIMITATION IMPORTANTE :**
- Seulement **1 Translator F0 par subscription Azure**
- Quota : 2.5M caractères/mois
- Soft-delete bloque création F0 pendant 48h

**Solution :** Le script `deploy.sh` gère automatiquement :
- Détection F0 existant → Option de réutilisation
- Détection soft-deleted → Option de purge
- Proposition passage à S1 si nécessaire

📖 **Détails :** `LIMITATIONS_AZURE_TRANSLATOR.md`

---

### 2. Connexion Blob Storage

**Requis pendant import Power Platform**

**Informations nécessaires :**
- Nom compte : `sttrad{client}`
- Clé d'accès : (voir `deployment-*.json`)

⚠️ **Ne pas oublier** de créer la connexion pendant l'import !

---

### 3. Variables d'Environnement

**À configurer dans Power Platform :**
```
Translator-key : (voir deployment-*.json)
Translator-url : https://api.cognitive.microsofttranslator.com
```

✅ **Vérifier** avant de tester le bot

---

## 🔒 Sécurité

### Fichiers Sensibles (Ne JAMAIS Committer)

- ❌ `deployment-*.json` (credentials Azure complètes)
- ❌ `connector-config-*.json` (Function Keys)
- ❌ Fichiers avec clés API

### Fichiers Safe

- ✅ Tous les `.md` (documentation)
- ✅ Scripts `.sh` et `.py`
- ✅ Images (captures d'écran)
- ✅ Solution `.zip`

**Le `.gitignore` est configuré pour bloquer les fichiers sensibles.**

---

## 📊 Métriques de Déploiement

### Durées Moyennes

| Phase | Durée |
|-------|-------|
| Préparation + Lecture docs | 30 min |
| Déploiement Azure | 30 min |
| Power Platform | 40 min |
| Publication Teams | 20 min |
| **TOTAL** | **~2h** |

*Note : Temps pour première fois. Déploiements suivants : ~1h*

### Taux de Réussite

**Avec cette documentation :** 100% ✅

> "Si c'est ma mère qui le fait, ça marche !" - PlumyCat

La documentation est conçue pour être suivie même par quelqu'un sans expérience.

---

## 🆘 En Cas de Problème

### Démarche de Résolution

1. **Consulter la section Troubleshooting** du guide concerné
2. **Vérifier les logs** (Azure ou Power Automate)
3. **Chercher dans l'INDEX** par problème spécifique
4. **Tester les endpoints** API

### Problèmes Fréquents

| Problème | Guide | Section |
|----------|-------|---------|
| Impossible créer F0 | `LIMITATIONS_AZURE_TRANSLATOR.md` | Tout le doc |
| API ne répond pas | `GUIDE_DEPLOIEMENT.md` | Troubleshooting |
| Import échoue | `GUIDE_POWER_PLATFORM_COMPLET.md` | Troubleshooting |
| Bot invisible Teams | `GUIDE_PUBLICATION_TEAMS.md` | Troubleshooting |
| Traduction échoue | Tous les guides | Test endpoints |

---

## 📞 Support et Resources

### Documentation

**Complète et à jour dans ce dépôt :**
- 15+ guides détaillés
- ~100 pages de documentation
- Scripts automatisés
- Captures d'écran

### Portails

- **Azure :** https://portal.azure.com
- **Copilot Studio :** https://copilotstudio.microsoft.com
- **Power Apps :** https://make.powerapps.com
- **Admin Teams :** https://admin.teams.microsoft.com

### Développeur

**Be-Cloud**
- Site : https://be-cloud.com

---

## 🎯 Checklist Avant de Commencer

### Préparation

- [ ] Lire `START_HERE.md`
- [ ] Lire `DEMARRAGE_COMPLET.md`
- [ ] ⚠️ Lire `LIMITATIONS_AZURE_TRANSLATOR.md`
- [ ] Vérifier prérequis (comptes, licences)
- [ ] Préparer icône bot (PNG 512x512px)

### Outils

- [ ] Azure CLI installé et configuré
- [ ] Python 3.12+ installé
- [ ] Git installé
- [ ] VM ou environnement de déploiement prêt

### Documentation

- [ ] Tous les guides téléchargés
- [ ] INDEX_DOCUMENTATION.md consulté
- [ ] Scripts testés

---

## ✅ Validation Finale

Après déploiement complet, vérifier :

### Backend Azure

- [ ] `curl {function_url}/api/health` retourne "healthy"
- [ ] Storage Account contient 2 containers
- [ ] Translator répond correctement
- [ ] Function App démarrée

### Power Platform

- [ ] Solution importée sans erreur
- [ ] Connexion Blob créée
- [ ] Variables configurées
- [ ] Bot répond en test local

### Teams

- [ ] Bot publié et approuvé
- [ ] Visible dans App Store Teams
- [ ] Test utilisateur standard réussi
- [ ] Document traduit avec succès

---

## 🎉 Succès de Déploiement

**Signes de réussite :**
- ✅ API retourne "healthy"
- ✅ Bot répond dans Copilot Studio
- ✅ Bot visible dans Teams
- ✅ Traduction de document fonctionne
- ✅ Utilisateurs peuvent accéder au bot
- ✅ Coûts Azure attendus (~14-16€/mois)

**Le bot est prêt à être utilisé par toute l'organisation ! 🚀**

---

## 📂 Rapports d'Intervention

Chaque déploiement client est documenté dans :
```
clients/{client}-{date}/RAPPORT_INTERVENTION.md
```

**Contenu :**
- Informations client (sans credentials)
- Ressources déployées
- Tests effectués
- Coûts
- Prochaines étapes

---

## 🔄 Mises à Jour

### Mise à Jour du Bot

**Pour mettre à jour le code de la Function :**
```bash
cd function_app
func azure functionapp publish func-translation-{client}
```

**Pour mettre à jour la solution Power Platform :**
1. Exporter solution modifiée
2. Importer en mode "Mise à jour"
3. Republier le bot

### Mise à Jour Documentation

La documentation est vivante et peut être améliorée :
- Ajouter captures d'écran
- Enrichir troubleshooting
- Ajouter cas d'usage

---

## 🌟 Fonctionnalités

### Formats (15+)

Word, PowerPoint, PDF, HTML, TXT, RTF, CSV, TSV, Outlook MSG, OpenDocument (ODT, ODP, ODS)

### Langues (100+)

Français, Anglais, Espagnol, Allemand, Italien, Portugais, Néerlandais, Polonais, Russe, Chinois, Japonais, Coréen, Arabe, etc.

### Capacités

- Détection automatique langue
- Préservation formatage
- Glossaires personnalisés
- Traduction asynchrone
- Intégration Teams native

---

**Version :** 1.0  
**Date :** 2026-01-08  
**Statut :** ✅ Production Ready  
**Taux de réussite :** 100%

---

**🚀 Bon déploiement !**

*"Documentation complète = Déploiement réussi"*
