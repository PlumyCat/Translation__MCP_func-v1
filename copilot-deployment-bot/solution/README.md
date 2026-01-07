# Solution Power Platform

Placez le fichier ZIP de la solution Copilot Studio dans ce dossier.

## Solution actuelle

**Fichier:** `BotCopilotTraducteur_1_0_0_2.zip`

Le code recherche automatiquement la solution dans:
1. `Solution/BotCopilotTraducteur_1_0_0_2.zip`
2. `solution/BotCopilotTraducteur_1_0_0_2.zip`

## Comment exporter une nouvelle version

1. Ouvrir Power Apps (https://make.powerapps.com)
2. Selectionner l'environnement de developpement
3. Aller dans Solutions
4. Selectionner la solution "Bot Copilot Traducteur"
5. Cliquer sur "Exporter"
6. Choisir "Non gere" ou "Gere" selon le besoin
7. Telecharger le fichier ZIP
8. Placer dans ce dossier

## Alternative avec pac CLI

```bash
# Se connecter a l'environnement de dev
pac auth create --environment https://votre-env.crm4.dynamics.com

# Exporter la solution
pac solution export --name BotCopilotTraducteur --path ./solution/ --managed
```

## Structure de la solution

La solution contient:
- Le bot Copilot Studio pour le deploiement
- Les topics de conversation
- Le Custom Connector pour le backend
- Les flux Power Automate (si applicable)
