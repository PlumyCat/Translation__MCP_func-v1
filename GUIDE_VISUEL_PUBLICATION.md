# 📸 Guide Visuel - Publication Rapide du Bot dans Teams

> Guide illustré pour publier rapidement le Bot Traducteur dans Microsoft Teams

---

## 🎯 Résumé en 9 Étapes

| # | Étape | Durée | Action |
|---|-------|-------|--------|
| 1 | Publier le bot | 2 min | Copilot Studio → Publier |
| 2 | Accéder aux canaux | 1 min | Canaux → Teams |
| 3 | Créer le canal | 1 min | Configurer Teams |
| 4 | Personnaliser | 5 min | Icône + Descriptions |
| 5 | Options disponibilité | 2 min | Toute l'organisation |
| 6 | Centre Admin | 2 min | Se connecter en admin |
| 7 | Approuver requête | 2 min | Autoriser le bot |
| 8 | Publier | 1 min | Sélectionner étendue |
| 9 | Épingler | 3 min | Configurer épinglage |

**Total : 15-20 minutes**

---

## 📋 ÉTAPE 1 : Publier dans Copilot Studio

```
Copilot Studio → Ouvrir le Bot → Cliquer "Publier" → Confirmer
```

✅ **Vérification :** Statut = "Publié"

---

## 📋 ÉTAPE 2-3 : Configurer le Canal Teams

```
Bot → Canaux → Teams et Microsoft 365 Copilot → Créer/Configurer
```

![Configuration du Canal Teams](images/Teams%20CopM365.png)

### 🔍 Ce que vous voyez :

1. **Case à cocher** : 
   - ✅ Rendre assistant disponible dans Microsoft 365 Copilot

2. **Version préliminaire de l'Assistant** :
   - Nom : **Traducteur**
   - Description : **Agent gérant la traduction de document**
   - Bouton : **"Modifier les détails"**

3. **Options de disponibilité** :
   - Option 1 : Afficher assistant dans Microsoft 365
   - Option 2 : Afficher assistant dans Teams

---

## 📋 ÉTAPE 4 : Personnaliser (Modifier les détails)

Cliquer sur **"Modifier les détails"**

### ✏️ À remplir :

#### **Icône du bot**
```
📁 Fichier : images/bot-icon.png
📐 Format : PNG 192x192px minimum
```

#### **Description Courte**
```
Agent gérant la traduction de document
```

#### **Description Moyenne**
```
Notre bot de traduction d'entreprise, propulsé par le service Azure Translator, 
offre une solution efficace pour traduire vos documents tout en préservant leur 
mise en forme originale. Compatible avec plus de 100 langues, il prend en charge 
une variété de formats de fichiers, notamment :

- Documents Microsoft Word (.docx)
- Présentations Microsoft PowerPoint (.pptx)
- Documents PDF (.pdf)
- Fichiers HTML (.html, .htm)
- Messages Outlook (.msg)
- Formats OpenDocument (.odt, .odp, .ods)
- Fichiers texte (.txt)
- Formats délimités (.csv, .tsv, .tab)
- Format RTF (.rtf)

Notre bot assure la conservation de la structure et du formatage de vos documents 
originaux, garantissant ainsi des traductions précises sans compromettre la 
présentation. Il détecte automatiquement la langue source et peut utiliser des 
glossaires personnalisés (CSV, TSV, XLIFF) pour adapter les traductions à votre 
entreprise.
```

#### **Section "Plus"**
```
Nom du développeur : Be-Cloud
Site web (optionnel) : https://be-cloud.com
```

**💾 Enregistrer les modifications**

---

## 📋 ÉTAPE 5 : Options de Disponibilité

![Options de Disponibilité](images/Demande%20pub.png)

### 🎯 Configuration recommandée

#### ✅ Option à sélectionner :

```
☑️ Afficher à tous les membres de mon organisation
   └─ ☑️ Disponible dans l'App Store
```

#### 📝 Texte affiché :
> "S'affiche dans **Créé par votre organisation** après approbation de l'administrateur"

### 📤 Actions disponibles :

1. **🔗 Obtenir un lien**
   - Copier le lien pour partage direct
   - Les utilisateurs peuvent ouvrir l'assistant dans Teams

2. **📦 Télécharger .zip**
   - Pour installation manuelle dans Teams
   - Pour soumission au store

3. **✅ Afficher dans le magasin**
   - Soumettre pour approbation admin
   - Publication à l'organisation

**🚀 Cliquer sur "Enregistrer" ou "Soumettre"**

---

## 📋 ÉTAPE 6-7 : Approbation Admin

### 🔐 Se Connecter au Centre Admin

```
URL : https://admin.teams.microsoft.com
Compte : Administrateur Microsoft 365
```

### 🔍 Naviguer vers les Requêtes

```
Menu → Applications Teams → Gérer les applications
```

**OU**

```
Menu → Applications Teams → Requêtes d'approbation
```

### 📋 Filtrer et Trouver le Bot

1. **Filtrer par état :**
   - État d'approbation : **"En attente d'approbation"**

2. **Rechercher :**
   - Nom : "Bot Traducteur" ou "Traducteur"
   - Développeur : "Be-Cloud"

3. **Cliquer sur le bot** pour voir les détails

### ✅ Examiner les Détails

- Nom : **Traducteur**
- Description : **Agent gérant la traduction de document**
- Développeur : **Be-Cloud**
- Permissions : Vérifier et valider

---

## 📋 ÉTAPE 8 : Publier à l'Organisation

### 🚀 Approuver et Publier

1. **Cliquer sur "Publier"** ou **"Autoriser"**
2. Une fenêtre s'ouvre : **"Publier à l'organisation"**

### 🎯 Configurer l'Étendue

**Sélectionner :**
```
☑️ Disponible pour tout le monde
```
**OU**
```
☑️ Organisation entière
```

3. **Cliquer sur "Suivant"**
4. **Confirmer en cliquant sur "Publier"**

✅ **Le bot est maintenant publié !**

---

## 📋 ÉTAPE 9 : Épingler le Bot (Optionnel mais recommandé)

### 📌 Pourquoi épingler ?

- Facilite l'accès pour les utilisateurs
- Bot visible directement dans la barre Teams
- Améliore l'adoption

### ⚙️ Configuration

```
Centre Admin Teams → Applications → Bot Traducteur → Affectations
```

**OU**

```
Centre Admin Teams → Stratégies d'application → Configuration
```

### 📝 Étapes :

1. **Modifier la stratégie "Global"**
   - Ou créer une nouvelle stratégie

2. **Applications épinglées**
   - Cliquer sur "Ajouter des applications"
   - Rechercher "Bot Traducteur"
   - Sélectionner et ajouter

3. **Étendue d'épinglage**
   ```
   ☑️ Organisation entière
   ```
   - Ou sélectionner groupes/utilisateurs spécifiques

4. **Position**
   - Déplacer le bot dans la liste
   - Position 1-5 = Très visible

5. **Enregistrer**

⏱️ **Propagation : jusqu'à 24 heures**

---

## ✅ Vérification Finale

### 🔍 Tests Admin

- [ ] Bot visible dans Centre Admin Teams
- [ ] Statut = **"Autorisé"** ou **"Publié"**
- [ ] Disponibilité = **"Toute l'organisation"**
- [ ] Épinglage configuré (si souhaité)

### 👤 Tests Utilisateur

```
Compte utilisateur standard → Teams → Applications → Rechercher "Bot Traducteur"
```

- [ ] Bot trouvé dans les résultats
- [ ] Cliquer "Ajouter"
- [ ] Conversation s'ouvre
- [ ] Envoyer "Bonjour"
- [ ] Bot répond correctement
- [ ] Télécharger un document test
- [ ] Traduction fonctionne
- [ ] Document traduit téléchargeable

---

## 🎉 Publication Terminée !

### 📊 Résumé des Actions

| Composant | Statut | Détails |
|-----------|--------|---------|
| **Bot** | ✅ Publié | Copilot Studio |
| **Canal Teams** | ✅ Configuré | Avec icône et descriptions |
| **Disponibilité** | ✅ Organisation | Toute l'entreprise |
| **Approbation** | ✅ Accordée | Par admin M365 |
| **Épinglage** | ✅ Activé | (Optionnel) |

### 📱 Accès Utilisateurs

**3 façons d'accéder au bot :**

1. **📌 Épinglé** (si configuré)
   - Visible dans barre latérale Teams
   - Clic direct

2. **🔍 Recherche**
   - Teams → Applications → "Bot Traducteur"
   - Ajouter → Utiliser

3. **🔗 Lien direct**
   - Partager le lien de l'assistant
   - Ouvre directement dans Teams

---

## 📞 Support

### ❓ Problèmes Fréquents

| Problème | Solution Rapide |
|----------|----------------|
| Bot pas visible | Vérifier approbation admin + attendre 24h |
| Épinglage absent | Vérifier stratégie Global + redémarrer Teams |
| Traduction échoue | Vérifier Azure Function + variables environnement |
| Permissions refusées | Revoir permissions dans Centre Admin |

### 📚 Guides Complets

- **Guide détaillé** : `GUIDE_PUBLICATION_TEAMS.md`
- **Guide Power Platform** : `GUIDE_POWER_PLATFORM_COMPLET.md`
- **Guide Azure** : `GUIDE_DEPLOIEMENT.md`

---

## 🎯 Prochaines Étapes

1. **📢 Communiquer**
   - Annoncer le lancement dans Teams
   - Envoyer email aux utilisateurs
   - Créer guide utilisateur simple

2. **📊 Surveiller**
   - Vérifier utilisation (Analytics Teams)
   - Collecter feedbacks
   - Monitorer erreurs

3. **🔄 Améliorer**
   - Analyser conversations
   - Enrichir réponses du bot
   - Ajouter nouvelles fonctionnalités

---

**Guide créé le** : 2026-01-08  
**Version** : 1.0  
**Type** : Guide Visuel Rapide avec Captures d'Écran
