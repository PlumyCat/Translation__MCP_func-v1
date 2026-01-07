# Guide de Deploiement Power Platform

Ce guide explique comment deployer la solution Copilot Studio "Bot Traducteur" chez un client.

---

## Prerequis

- Acces admin au tenant Power Platform du client
- Le fichier solution : `Solution/BotCopilotTraducteur_1_0_0_2.zip`
- L'URL de l'Azure Function deployee (depuis le bot de deploiement)

---

## Etape 1 : Verifier/Activer Dataverse

### 1.1 Acceder au Power Platform Admin Center

1. Aller sur https://admin.powerplatform.microsoft.com
2. Se connecter avec un compte admin du tenant client

### 1.2 Verifier si Dataverse est active

1. Menu gauche > **Environnements**
2. Trouver l'environnement cible (ex: "Production" ou "Default")
3. Cliquer dessus pour voir les details

**Si vous voyez une URL Dataverse** (ex: `https://org123.crm4.dynamics.com`) :
- Dataverse est deja active, passez a l'Etape 2

**Si pas d'URL Dataverse** :
- Continuez avec 1.3

### 1.3 Activer Dataverse (si necessaire)

1. Dans les details de l'environnement, cliquer **Ajouter une base de donnees** ou **Add Dataverse**
2. Configurer :
   - **Langue** : Francais (1036) ou Anglais (1033)
   - **Devise** : EUR
   - **Activer les apps Dynamics 365** : Non (sauf si necessaire)
3. Cliquer **Enregistrer**
4. Attendre 5-10 minutes pour le provisionnement

---

## Etape 2 : Importer la Solution

### 2.1 Acceder a Power Apps

1. Aller sur https://make.powerapps.com
2. Se connecter avec le compte admin
3. Verifier que l'environnement correct est selectionne (en haut a droite)

### 2.2 Importer la solution

1. Menu gauche > **Solutions**
2. Cliquer **Importer une solution** (ou "Import solution")
3. Cliquer **Parcourir** et selectionner `BotCopilotTraducteur_1_0_0_2.zip`
4. Cliquer **Suivant**
5. Verifier les composants importes
6. Cliquer **Importer**
7. Attendre la fin de l'import (peut prendre 2-5 minutes)

### 2.3 Verifier l'import

1. La solution "Bot Copilot Traducteur" devrait apparaitre dans la liste
2. Cliquer dessus pour voir les composants :
   - Le bot Copilot
   - Les connecteurs personnalises
   - Les flux (si presents)

---

## Etape 3 : Configurer le Bot

### 3.1 Ouvrir Copilot Studio

1. Aller sur https://copilotstudio.microsoft.com
2. Se connecter avec le compte admin
3. Selectionner le bon environnement

### 3.2 Configurer le connecteur

1. Trouver le bot "Traducteur" dans la liste
2. Ouvrir les parametres du connecteur personnalise
3. Mettre a jour l'URL de base avec l'URL de l'Azure Function :
   ```
   https://<function-app-name>.azurewebsites.net/api
   ```
4. Configurer l'authentification :
   - Type : API Key
   - Nom du parametre : `x-functions-key`
   - Valeur : La cle API de la function

### 3.3 Tester le bot

1. Ouvrir le bot dans Copilot Studio
2. Utiliser le panneau de test a droite
3. Tester une conversation basique

---

## Etape 4 : Publier le Bot

### 4.1 Publication

1. Dans Copilot Studio, ouvrir le bot
2. Cliquer **Publier** en haut a droite
3. Confirmer la publication

### 4.2 Configurer les canaux (optionnel)

Selon les besoins du client :
- **Teams** : Ajouter le bot a Microsoft Teams
- **Site web** : Generer le widget d'integration
- **Autres** : Slack, Facebook, etc.

---

## Depannage

### "La solution ne s'importe pas"
- Verifier que Dataverse est bien active
- Verifier la version de la solution
- Essayer d'importer en mode "Ecraser" si une version existe deja

### "Le connecteur ne fonctionne pas"
- Verifier l'URL de l'Azure Function
- Tester l'URL directement : `https://<url>/api/health`
- Verifier la cle API

### "Erreur d'authentification"
- Regenerer la cle API de l'Azure Function
- Mettre a jour le connecteur avec la nouvelle cle

---

## Checklist finale

- [ ] Dataverse active dans l'environnement
- [ ] Solution importee avec succes
- [ ] URL du connecteur configuree
- [ ] Cle API configuree
- [ ] Bot teste et fonctionnel
- [ ] Bot publie
- [ ] Canal(aux) configure(s) selon besoin client
