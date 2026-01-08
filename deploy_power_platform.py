#!/usr/bin/env python3
"""
Guide de déploiement Power Platform pour le Bot Traducteur
Prépare toutes les informations nécessaires pour l'import manuel ou automatique
"""

import os
import sys
import json
from pathlib import Path

# Couleurs
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_step(step: str):
    print(f"{Colors.BOLD}➤ {step}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    print(f"  {message}")

def load_deployment_info():
    """Charge les informations du dernier déploiement Azure"""
    # Chercher le fichier de déploiement le plus récent
    deployment_files = sorted(Path('.').glob('deployment-*.json'), reverse=True)
    
    if not deployment_files:
        print_warning("Aucun fichier de déploiement trouvé")
        print_info("Exécutez d'abord: ./deploy.sh")
        return None
    
    deployment_file = deployment_files[0]
    print_success(f"Fichier de déploiement trouvé: {deployment_file}")
    
    with open(deployment_file, 'r') as f:
        return json.load(f)

def check_solution_file():
    """Vérifie que le fichier solution existe"""
    solution_path = Path('Solution')
    solution_files = list(solution_path.glob('*.zip'))
    
    if not solution_files:
        print_warning("Aucun fichier solution trouvé dans Solution/")
        return None
    
    solution_file = solution_files[0]
    print_success(f"Solution trouvée: {solution_file}")
    return solution_file

def generate_connector_config(deployment_info):
    """Génère la configuration pour le connecteur personnalisé"""
    config = {
        "name": "Translation Service Connector",
        "description": f"Connecteur pour {deployment_info['client_name']}",
        "host": deployment_info['function_app_url'].replace('https://', ''),
        "base_url": deployment_info['function_app_url'],
        "authentication": {
            "type": "api_key",
            "header_name": "code",
            "header_value": deployment_info.get('function_key', '<À_RÉCUPÉRER>')
        },
        "endpoints": deployment_info['endpoints']
    }
    
    return config

def print_manual_deployment_guide(deployment_info, solution_file, connector_config):
    """Affiche le guide de déploiement manuel détaillé"""
    
    print_header("GUIDE DE DÉPLOIEMENT POWER PLATFORM")
    
    print_step("ÉTAPE 1 : Préparer les informations")
    print_info(f"Client: {deployment_info['client_name']}")
    print_info(f"Tenant: {deployment_info['tenant_id']}")
    print_info(f"URL API: {deployment_info['function_app_url']}")
    print_info(f"Fichier solution: {solution_file}")
    
    print()
    print_step("ÉTAPE 2 : Se connecter à Power Platform")
    print_info("1. Ouvrir un navigateur")
    print_info("2. Aller sur: https://make.powerapps.com")
    print_info("3. Se connecter avec le compte du client")
    print_info(f"   User: {deployment_info.get('deployed_by', 'compte-client@domain.com')}")
    
    print()
    print_step("ÉTAPE 3 : Vérifier/Créer l'environnement")
    print_info("1. En haut à droite, vérifier l'environnement actif")
    print_info("2. Si pas d'environnement Dataverse:")
    print_info("   a. Aller dans Admin center: https://admin.powerplatform.microsoft.com")
    print_info("   b. Environments → New")
    print_info("   c. Nom: 'Production - Bot Traducteur'")
    print_info("   d. Région: France")
    print_info("   e. Type: Production")
    print_info("   f. Activer Dataverse: Yes")
    print_info("   g. Langue: Français / Monnaie: EUR")
    
    print()
    print_step("ÉTAPE 4 : Importer la solution")
    print_info("1. Dans Power Apps, aller dans 'Solutions'")
    print_info("2. Cliquer sur 'Import solution'")
    print_info("3. Cliquer sur 'Browse'")
    print_info(f"4. Sélectionner: {solution_file.absolute()}")
    print_info("5. Cliquer sur 'Next'")
    print_info("6. Vérifier les informations et cliquer sur 'Import'")
    print_info("7. Attendre la fin de l'import (2-5 minutes)")
    
    print()
    print_step("ÉTAPE 5 : Configurer le connecteur personnalisé")
    print_info("1. Dans Solutions, ouvrir 'Bot Copilot Traducteur'")
    print_info("2. Aller dans 'Connecteurs personnalisés'")
    print_info("3. Ouvrir le connecteur 'Translation Service'")
    print_info("4. Dans l'onglet 'Security':")
    print_info("   - Authentication type: API Key")
    print_info("   - Parameter label: Function Key")
    print_info("   - Parameter name: code")
    print_info("   - Parameter location: Query")
    print_info("5. Dans l'onglet 'Definition':")
    print_info(f"   - Host: {connector_config['host']}")
    print_info(f"   - Base URL: {connector_config['base_url']}")
    print_info("6. Sauvegarder")
    
    print()
    print_step("ÉTAPE 6 : Créer une connexion")
    print_info("1. Dans Solutions, aller dans 'Connexions'")
    print_info("2. Cliquer sur 'New connection'")
    print_info("3. Chercher 'Translation Service'")
    print_info("4. Entrer la Function Key:")
    print_info(f"   {deployment_info.get('function_key', '<RÉCUPÉRER_DEPUIS_deployment.json>')}")
    print_info("5. Tester la connexion")
    
    print()
    print_step("ÉTAPE 7 : Configurer le bot Copilot Studio")
    print_info("1. Ouvrir Copilot Studio: https://copilotstudio.microsoft.com")
    print_info("2. Sélectionner le bot 'Bot Traducteur'")
    print_info("3. Aller dans 'Settings' → 'Bot details'")
    print_info("4. Vérifier la langue et description")
    print_info("5. Aller dans 'Topics'")
    print_info("6. Ouvrir le topic 'translate_document'")
    print_info("7. Vérifier que les actions utilisent la bonne connexion")
    
    print()
    print_step("ÉTAPE 8 : Tester le bot")
    print_info("1. Dans Copilot Studio, cliquer sur 'Test' en haut")
    print_info("2. Essayer une conversation:")
    print_info("   'Je veux traduire un document'")
    print_info("3. Vérifier que le bot répond correctement")
    print_info("4. Tester l'upload d'un fichier")
    
    print()
    print_step("ÉTAPE 9 : Publier le bot")
    print_info("1. Cliquer sur 'Publish' en haut à droite")
    print_info("2. Choisir les canaux de publication:")
    print_info("   - Demo website (pour tester)")
    print_info("   - Microsoft Teams (pour les utilisateurs)")
    print_info("   - Autre (selon besoins)")
    print_info("3. Cliquer sur 'Publish'")
    print_info("4. Attendre la fin de la publication")
    
    print()
    print_success("Déploiement Power Platform terminé !")

def save_connector_config(connector_config, deployment_info):
    """Sauvegarde la configuration du connecteur dans un fichier"""
    filename = f"connector-config-{deployment_info['client_name']}.json"
    with open(filename, 'w') as f:
        json.dump(connector_config, f, indent=2)
    print_success(f"Configuration du connecteur sauvegardée: {filename}")

def create_deployment_checklist(deployment_info):
    """Crée une checklist de déploiement"""
    checklist = f"""
# Checklist Déploiement Power Platform - {deployment_info['client_name']}

## Préparation
- [ ] Fichier solution disponible
- [ ] Informations Azure Function récupérées
- [ ] Compte Power Platform du client actif
- [ ] Environnement Dataverse créé/vérifié

## Import
- [ ] Solution importée dans Power Apps
- [ ] Import terminé sans erreur
- [ ] Solution visible dans la liste

## Configuration
- [ ] Connecteur personnalisé configuré
  - [ ] Host: {deployment_info['function_app_url']}
  - [ ] Authentication: API Key (code)
- [ ] Connexion créée avec la Function Key
- [ ] Connexion testée avec succès

## Bot Copilot Studio
- [ ] Bot visible dans Copilot Studio
- [ ] Topics chargés correctement
- [ ] Topic 'translate_document' fonctionnel
- [ ] Actions liées au connecteur configurées
- [ ] Test du bot réussi

## Publication
- [ ] Bot publié
- [ ] Canal Demo website activé
- [ ] Canal Teams activé (si applicable)
- [ ] URL du bot fournie au client

## Tests Finaux
- [ ] Upload d'un document test
- [ ] Traduction effectuée
- [ ] Document traduit téléchargé
- [ ] Client formé à l'utilisation

## Documentation
- [ ] Guide utilisateur fourni
- [ ] Informations de connexion transmises
- [ ] Support technique défini

---
Déploiement effectué le: {deployment_info.get('deployed_at', 'N/A')}
Par: {deployment_info.get('deployed_by', 'N/A')}
"""
    
    filename = f"checklist-power-platform-{deployment_info['client_name']}.md"
    with open(filename, 'w') as f:
        f.write(checklist)
    print_success(f"Checklist créée: {filename}")

def main():
    print_header("DÉPLOIEMENT POWER PLATFORM")
    print_info("Préparation du déploiement du Bot Copilot Studio")
    
    # Charger les infos de déploiement Azure
    deployment_info = load_deployment_info()
    if not deployment_info:
        sys.exit(1)
    
    print()
    
    # Vérifier le fichier solution
    solution_file = check_solution_file()
    if not solution_file:
        sys.exit(1)
    
    print()
    
    # Générer la config du connecteur
    connector_config = generate_connector_config(deployment_info)
    save_connector_config(connector_config, deployment_info)
    
    print()
    
    # Créer la checklist
    create_deployment_checklist(deployment_info)
    
    print()
    
    # Afficher le guide
    print_manual_deployment_guide(deployment_info, solution_file, connector_config)
    
    print()
    print_header("INFORMATIONS IMPORTANTES")
    print_info(f"URL API: {deployment_info['function_app_url']}")
    print_info(f"Function Key: {deployment_info.get('function_key', '<VOIR deployment.json>')}")
    print_info(f"Tenant: {deployment_info['tenant_id']}")
    print()
    print_warning("IMPORTANT: Ces informations sont sensibles !")
    print_warning("Ne pas les partager publiquement")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Opération annulée{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Erreur: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
