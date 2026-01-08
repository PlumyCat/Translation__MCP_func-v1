# ⚠️ Limitations Azure Translator - Guide Complet

## 🔴 Limitation SKU F0 (Free)

### Règle Principale
**Une seule instance Translator F0 par subscription Azure**

Cette limitation signifie que :
- ✅ Vous pouvez créer **UN SEUL** Translator F0 dans toute votre subscription
- ❌ Impossible de créer un 2ème Translator F0, même dans un Resource Group différent
- ✅ Vous pouvez créer autant de Translator S1/S2/S3 que vous voulez

### Ce que le SKU F0 offre
- ✅ **2.5 millions de caractères** par mois GRATUITS
- ✅ Toutes les langues supportées (50+)
- ✅ Tous les formats de documents
- ✅ API complète identique à S1

---

## 🗑️ Problème du Soft-Delete

### Qu'est-ce que le Soft-Delete ?

Quand vous supprimez un Translator avec `az cognitiveservices account delete`, il n'est **pas immédiatement supprimé définitivement**. Il passe en état "**soft-deleted**" (suppression douce).

### Conséquences

❌ **Un Translator F0 en soft-delete BLOQUE la création d'un nouveau F0**

Même si vous avez supprimé votre Translator F0, vous ne pouvez pas en créer un nouveau tant qu'il est en soft-delete !

### Durée du Soft-Delete

Les Translator soft-deleted restent dans cet état pendant **48 heures** avant d'être purgés automatiquement.

---

## 🔧 Solutions Gérées par le Script

Le script `deploy_client.py` gère automatiquement ces cas :

### 1. Détection d'un F0 existant

```
➤ Vérification des Translator existants
⚠ Un Translator F0 existe déjà: translator-autre-client
  Resource Group: rg-translation-autre-client
  ⚠️  Limitation: Une seule instance F0 par subscription Azure

Voulez-vous réutiliser ce Translator existant? (o/n):
```

**Options :**
- **Oui** : Réutilise le Translator existant (recommandé)
- **Non** : Propose 3 choix :
  1. Supprimer manuellement et relancer
  2. Utiliser SKU S1 (payant)
  3. Annuler

### 2. Détection de Translator soft-deleted

```
➤ Vérification des Translator en soft-delete
⚠ Trouvé 1 Translator(s) en soft-delete:
  1. translator-old (supprimé le 2026-01-08)

⚠️  Les Translator F0 soft-deleted bloquent la création de nouveaux F0
Il faut les purger définitivement (irréversible !)

Voulez-vous purger ces Translator? (o/n):
```

**Options :**
- **Oui** : Purge définitivement (irréversible)
- **Non** : Continue sans créer de nouveau Translator

---

## 📋 Scénarios Courants

### Scénario 1 : Première installation (subscription vierge)

✅ **Tout fonctionne automatiquement**
```bash
./deploy.sh
# → Crée un Translator F0 sans problème
```

### Scénario 2 : Un F0 existe déjà ailleurs

⚠️ **Le script détecte le F0 existant**

**Option A (Recommandée)** : Réutiliser
- Tous les clients partagent le même Translator
- Coût : 0€
- Limitation : 2.5M caractères/mois partagés

**Option B** : Supprimer l'ancien
```bash
# Supprimer le Translator existant
az cognitiveservices account delete \
  --name translator-ancien \
  --resource-group rg-translation-ancien

# Purger immédiatement
az cognitiveservices account purge \
  --name translator-ancien \
  --resource-group rg-translation-ancien \
  --location global

# Attendre 30 secondes puis relancer
sleep 30
./deploy.sh
```

**Option C** : Utiliser S1 (payant)
- Coût : +10€/mois par client
- Quota : 2M caractères/mois PAR client

### Scénario 3 : Déploiements multiples clients

#### Approche 1 : Translator partagé (Recommandé pour F0)

```
Subscription Azure
├── RG client-1
│   ├── Storage
│   ├── Function App
│   └── (pas de Translator)
├── RG client-2
│   ├── Storage
│   ├── Function App
│   └── (pas de Translator)
└── RG shared
    └── Translator F0 (partagé)
```

**Avantages :**
- ✅ Coût : 0€
- ✅ Un seul Translator pour tous

**Inconvénients :**
- ⚠️ Quota partagé (2.5M chars/mois total)
- ⚠️ Gestion manuelle de la clé

**Configuration :**
```bash
# Lors du déploiement, réutiliser le Translator existant
./deploy.sh
# → Répondre "o" quand demandé
```

#### Approche 2 : Translator S1 par client

```
Subscription Azure
├── RG client-1
│   ├── Storage
│   ├── Function App
│   └── Translator S1
├── RG client-2
│   ├── Storage
│   ├── Function App
│   └── Translator S1
└── RG client-3
    ├── Storage
    ├── Function App
    └── Translator S1
```

**Avantages :**
- ✅ Quota dédié par client (2M chars/mois)
- ✅ Isolation complète
- ✅ Facturation séparée

**Inconvénients :**
- ❌ Coût : +10€/mois par client

**Configuration :**
```bash
# Lors du déploiement, choisir S1
./deploy.sh
# → Répondre "2" (Utiliser SKU S1)
```

### Scénario 4 : Nettoyage/Tests multiples

⚠️ **Attention au soft-delete !**

```bash
# Déploiement test 1
./deploy.sh
# → OK, Translator F0 créé

# Suppression
az group delete --name rg-translation-test1 --yes
# ⚠️  Translator passe en soft-delete

# Déploiement test 2 (dans les 48h)
./deploy.sh
# ❌ ERREUR: Impossible de créer F0 (soft-delete existant)
```

**Solution :**
```bash
# Purger immédiatement après suppression
az cognitiveservices account list-deleted

az cognitiveservices account purge \
  --name translator-test1 \
  --resource-group rg-translation-test1 \
  --location global

# Attendre 30 secondes
sleep 30

# Relancer
./deploy.sh
```

---

## 🛠️ Commandes Utiles

### Lister tous les Translator de la subscription
```bash
az cognitiveservices account list \
  --query "[?kind=='TextTranslation'].{Name:name, SKU:sku.name, RG:resourceGroup}" \
  -o table
```

### Lister les Translator F0 uniquement
```bash
az cognitiveservices account list \
  --query "[?kind=='TextTranslation' && sku.name=='F0'].{Name:name, RG:resourceGroup}" \
  -o table
```

### Lister les Translator soft-deleted
```bash
az cognitiveservices account list-deleted \
  --query "[?kind=='TextTranslation']" \
  -o table
```

### Purger un Translator soft-deleted
```bash
az cognitiveservices account purge \
  --name <TRANSLATOR_NAME> \
  --resource-group <RESOURCE_GROUP> \
  --location global
```

### Supprimer ET purger immédiatement
```bash
# Supprimer
az cognitiveservices account delete \
  --name translator-test \
  --resource-group rg-translation-test

# Purger
az cognitiveservices account purge \
  --name translator-test \
  --resource-group rg-translation-test \
  --location global
```

---

## 💡 Recommandations

### Pour Environnement de Production

**Option 1 : Translator F0 partagé (Petits clients)**
- ✅ Si volume < 2.5M chars/mois total
- ✅ Coût : 0€
- ⚠️ Quota partagé entre tous les clients

**Option 2 : Translator S1 par client (Gros clients)**
- ✅ Si besoin d'isolation ou volume > 2.5M chars/mois
- ✅ Quota dédié : 2M chars/mois par client
- ❌ Coût : +10€/mois par client

### Pour Tests/Développement

⚠️ **Attention au soft-delete !**

1. Créer un Translator F0 dédié aux tests
2. Le réutiliser pour tous les tests
3. Ne PAS le supprimer entre les tests
4. Si suppression nécessaire : **toujours purger immédiatement**

```bash
# Script de test avec nettoyage complet
./deploy.sh

# Tests...

# Nettoyage complet avec purge
TRANSLATOR_NAME=$(az cognitiveservices account list \
  --resource-group rg-translation-test \
  --query "[0].name" -o tsv)

az group delete --name rg-translation-test --yes

az cognitiveservices account purge \
  --name $TRANSLATOR_NAME \
  --resource-group rg-translation-test \
  --location global
```

---

## 📊 Comparaison SKU

| Caractéristique | F0 (Free) | S1 (Standard) |
|----------------|-----------|---------------|
| **Coût** | 0€/mois | ~10€/mois |
| **Quota** | 2.5M chars/mois | 2M chars/mois |
| **Instances** | **1 par subscription** | Illimité |
| **Soft-delete** | Bloque nouveau F0 | N'affecte pas |
| **Langues** | Toutes | Toutes |
| **Performance** | Standard | Standard |
| **Support** | Community | Standard |

---

## ✅ Checklist Déploiement

### Avant le déploiement
- [ ] Vérifier les Translator existants
- [ ] Vérifier les Translator soft-deleted
- [ ] Décider : F0 partagé ou S1 par client ?

### Pendant le déploiement
- [ ] Le script détecte-t-il un F0 existant ?
  - [ ] Oui → Réutiliser ou S1 ?
  - [ ] Non → Continuer avec F0
- [ ] Le script détecte-t-il du soft-delete ?
  - [ ] Oui → Purger ou attendre 48h ?
  - [ ] Non → Continuer

### Après le déploiement
- [ ] Vérifier le SKU créé (F0 ou S1)
- [ ] Noter le nom du Translator
- [ ] Documenter la décision (partagé/dédié)

---

## 🆘 Dépannage

### Erreur : "Cannot create more than 1 F0 account"

**Cause :** Un F0 existe déjà

**Solutions :**
1. Réutiliser l'existant
2. Supprimer + purger l'ancien
3. Utiliser S1

### Erreur : "Account with name X already exists in deleted state"

**Cause :** Translator en soft-delete

**Solutions :**
1. Purger : `az cognitiveservices account purge ...`
2. Attendre 48h
3. Utiliser un autre nom
4. Utiliser S1

### Erreur après purge : "Still cannot create F0"

**Cause :** Propagation non terminée

**Solution :**
```bash
# Attendre plus longtemps
sleep 60

# Réessayer
./deploy.sh
```

---

**Document mis à jour : 2026-01-08**  
**Version : 1.0 - Guide complet**
