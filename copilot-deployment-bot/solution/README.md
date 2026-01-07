# Solution Power Platform

Placez le fichier ZIP de la solution Copilot Studio dans ce dossier.

## Nom attendu

Le fichier doit s'appeler: `TranslationDeploymentBot.zip`

## Comment exporter la solution

1. Ouvrir Power Apps (https://make.powerapps.com)
2. Selectionner l'environnement de developpement
3. Aller dans Solutions
4. Selectionner la solution "Translation Deployment Bot"
5. Cliquer sur "Exporter"
6. Choisir "Non gere" ou "Gere" selon le besoin
7. Telecharger le fichier ZIP
8. Renommer en `TranslationDeploymentBot.zip`
9. Placer dans ce dossier

## Alternative avec pac CLI

```bash
# Se connecter a l'environnement de dev
pac auth create --environment https://votre-env.crm4.dynamics.com

# Exporter la solution
pac solution export --name TranslationDeploymentBot --path ./solution/ --managed
```

## Structure de la solution

La solution devrait contenir:
- Le bot Copilot Studio
- Les topics de conversation
- Le Custom Connector pour le backend
- Les flux Power Automate (si applicable)
