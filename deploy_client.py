#!/usr/bin/env python3
"""
Script de déploiement interactif pour le Bot Traducteur
Prérequis: Exécuter setup_vm.sh en tant que root avant la première utilisation
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

# Couleurs pour le terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_step(step: str):
    """Affiche une étape"""
    print(f"{Colors.BOLD}➤ {step}{Colors.END}")

def print_success(message: str):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    """Affiche un avertissement"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    """Affiche une information"""
    print(f"  {message}")

def run_command(cmd: str, description: str = "", check: bool = True, capture: bool = False) -> Tuple[bool, str]:
    """Exécute une commande shell"""
    if description:
        print_step(description)
    
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                capture_output=True,
                text=True
            )
            return True, result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, check=check)
            return result.returncode == 0, ""
    except subprocess.CalledProcessError as e:
        if capture:
            return False, str(e)
        return False, ""

def check_prerequisites() -> bool:
    """Vérifie que tous les outils sont installés"""
    print_header("VÉRIFICATION DES PRÉREQUIS")
    
    tools = {
        "Azure CLI": "az --version",
        "Azure Functions Core Tools": "func --version",
        "Power Platform CLI": "pac --version",
        "Python 3": "python3 --version",
        "Git": "git --version"
    }
    
    all_ok = True
    for tool, cmd in tools.items():
        success, output = run_command(cmd, check=False, capture=True)
        if success:
            version = output.split('\n')[0]
            print_success(f"{tool}: {version}")
        else:
            print_error(f"{tool}: Non installé")
            all_ok = False
    
    if not all_ok:
        print_error("\nCertains outils sont manquants.")
        print_info("Exécutez d'abord: sudo bash setup_vm.sh")
        print_info("Puis rechargez votre shell: source ~/.bashrc")
        return False
    
    print_success("\nTous les prérequis sont installés !")
    return True

def check_azure_login() -> bool:
    """Vérifie si l'utilisateur est connecté à Azure"""
    print_header("VÉRIFICATION CONNEXION AZURE")
    
    success, output = run_command("az account show", check=False, capture=True)
    
    if success:
        try:
            account = json.loads(output)
            print_success(f"Connecté à Azure")
            print_info(f"Subscription: {account['name']}")
            print_info(f"Tenant: {account['tenantId']}")
            print_info(f"User: {account['user']['name']}")
            return True
        except:
            pass
    
    print_warning("Vous n'êtes pas connecté à Azure")
    print_info("\nConnectez-vous avec le compte du client:")
    
    response = input(f"\n{Colors.BOLD}Voulez-vous vous connecter maintenant? (o/n): {Colors.END}").lower()
    if response == 'o':
        success, _ = run_command("az login")
        return success
    
    return False

def sanitize_name(name: str) -> str:
    """Nettoie un nom pour le rendre compatible Azure"""
    # Enlever les caractères spéciaux, garder lettres, chiffres et tirets
    clean = re.sub(r'[^a-z0-9-]', '', name.lower())
    return clean

def collect_deployment_info() -> Optional[Dict]:
    """Collecte les informations de déploiement de manière interactive"""
    print_header("CONFIGURATION DU DÉPLOIEMENT")
    
    config = {}
    
    # Nom du client
    while True:
        client_name = input(f"{Colors.BOLD}Nom du client (ex: contoso, acme-corp): {Colors.END}").strip()
        if client_name:
            config['client_name'] = sanitize_name(client_name)
            if config['client_name'] != client_name:
                print_warning(f"Nom nettoyé: {config['client_name']}")
            break
        print_error("Le nom du client est obligatoire")
    
    # Région Azure
    print(f"\n{Colors.BOLD}Régions disponibles:{Colors.END}")
    regions = [
        ("1", "francecentral", "France Central (Recommandé)"),
        ("2", "westeurope", "West Europe"),
        ("3", "northeurope", "North Europe"),
        ("4", "eastus", "East US"),
        ("5", "westus", "West US")
    ]
    
    for num, code, name in regions:
        print(f"  {num}. {name}")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Choisissez une région (1-5): {Colors.END}").strip()
        if choice in ['1', '2', '3', '4', '5']:
            config['region'] = regions[int(choice)-1][1]
            break
        print_error("Choix invalide")
    
    # Génération des noms de ressources
    config['resource_group'] = f"rg-translation-{config['client_name']}"
    clean_name = config['client_name'].replace('-', '')[:15]
    config['storage_account'] = f"sttrad{clean_name}"
    config['translator_name'] = f"translator-{config['client_name']}"
    config['function_app'] = f"func-translation-{config['client_name']}"
    config['app_service_plan'] = f"asp-translation-{config['client_name']}"
    
    # OneDrive (optionnel)
    print(f"\n{Colors.BOLD}Intégration OneDrive (optionnel):{Colors.END}")
    response = input("Activer l'intégration OneDrive? (o/n): ").lower()
    config['enable_onedrive'] = response == 'o'
    
    if config['enable_onedrive']:
        print_warning("L'intégration OneDrive nécessite une App Registration Azure AD")
        config['onedrive_client_id'] = input("Client ID OneDrive: ").strip()
        config['onedrive_client_secret'] = input("Client Secret OneDrive: ").strip()
        config['onedrive_tenant_id'] = input("Tenant ID OneDrive: ").strip()
        config['onedrive_folder'] = input("Dossier OneDrive (défaut: Translated_Documents): ").strip() or "Translated_Documents"
    
    # Résumé
    print_header("RÉSUMÉ DU DÉPLOIEMENT")
    print_info(f"Client: {config['client_name']}")
    print_info(f"Région: {config['region']}")
    print_info(f"Resource Group: {config['resource_group']}")
    print_info(f"Storage Account: {config['storage_account']}")
    print_info(f"Translator: {config['translator_name']}")
    print_info(f"Function App: {config['function_app']}")
    print_info(f"OneDrive: {'Activé' if config['enable_onedrive'] else 'Désactivé'}")
    
    print(f"\n{Colors.BOLD}Confirmez-vous ces informations? (o/n): {Colors.END}", end='')
    response = input().lower()
    
    if response != 'o':
        print_warning("Déploiement annulé")
        return None
    
    return config

def create_resource_group(config: Dict) -> bool:
    """Crée le Resource Group"""
    cmd = f"az group create --name {config['resource_group']} --location {config['region']} --tags application=translation-service client={config['client_name']}"
    success, _ = run_command(cmd, "Création du Resource Group")
    if success:
        print_success(f"Resource Group créé: {config['resource_group']}")
    return success

def create_storage_account(config: Dict) -> bool:
    """Crée le Storage Account avec les containers"""
    # Créer le storage account
    cmd = f"""az storage account create \
        --name {config['storage_account']} \
        --resource-group {config['resource_group']} \
        --location {config['region']} \
        --sku Standard_LRS \
        --kind StorageV2 \
        --tags application=translation-service client={config['client_name']}"""
    
    success, _ = run_command(cmd, "Création du Storage Account")
    if not success:
        return False
    
    print_success(f"Storage Account créé: {config['storage_account']}")
    
    # Récupérer la clé
    cmd = f"az storage account keys list --resource-group {config['resource_group']} --account-name {config['storage_account']} --query '[0].value' -o tsv"
    success, storage_key = run_command(cmd, capture=True)
    if not success:
        return False
    
    config['storage_key'] = storage_key
    
    # Créer les containers
    for container in ['doc-to-trad', 'doc-trad']:
        cmd = f"az storage container create --name {container} --account-name {config['storage_account']} --account-key {storage_key}"
        success, _ = run_command(cmd)
        if success:
            print_success(f"Container créé: {container}")
        else:
            return False
    
    return True

def create_translator(config: Dict) -> bool:
    """Crée le service Azure Translator (gère F0 existant et soft-deleted)"""
    
    # Initialiser le SKU par défaut
    sku = "F0"
    
    print_step("Vérification des Translator existants")
    
    # 1. Vérifier si un Translator F0 existe déjà dans la subscription
    cmd = "az cognitiveservices account list --query \"[?kind=='TextTranslation' && sku.name=='F0'].{name:name, resourceGroup:resourceGroup}\" -o json"
    success, existing_f0 = run_command(cmd, capture=True)
    
    if success and existing_f0:
        try:
            import json
            existing = json.loads(existing_f0)
            if existing:
                existing_translator = existing[0]
                print_warning(f"Un Translator F0 existe déjà: {existing_translator['name']}")
                print_info(f"Resource Group: {existing_translator['resourceGroup']}")
                print_info("⚠️  Limitation: Une seule instance F0 par subscription Azure")
                
                response = input(f"\n{Colors.BOLD}Voulez-vous réutiliser ce Translator existant? (o/n): {Colors.END}").lower()
                if response == 'o':
                    config['translator_name'] = existing_translator['name']
                    config['translator_resource_group'] = existing_translator['resourceGroup']
                    
                    # Récupérer la clé
                    cmd = f"az cognitiveservices account keys list --name {config['translator_name']} --resource-group {existing_translator['resourceGroup']} --query 'key1' -o tsv"
                    success, translator_key = run_command(cmd, capture=True)
                    if success:
                        config['translator_key'] = translator_key
                        config['translator_endpoint'] = "https://api.cognitive.microsofttranslator.com"
                        config['sku_translator'] = "F0"
                        print_success(f"Translator existant réutilisé: {config['translator_name']}")
                        return True
                else:
                    print_warning("Création impossible avec F0. Options:")
                    print_info("1. Supprimer le Translator F0 existant")
                    print_info("2. Utiliser SKU S1 (payant: ~10€/mois)")
                    print_info("3. Annuler et réutiliser l'existant")
                    
                    choice = input(f"\n{Colors.BOLD}Votre choix (1/2/3): {Colors.END}").strip()
                    
                    if choice == "1":
                        print_warning("Supprimez manuellement le Translator et relancez le script")
                        print_info(f"Commande: az cognitiveservices account delete --name {existing_translator['name']} --resource-group {existing_translator['resourceGroup']}")
                        return False
                    elif choice == "2":
                        print_info("Création avec SKU S1...")
                        sku = "S1"
                    else:
                        return False
        except:
            pass
    
    # 2. Vérifier si un Translator soft-deleted existe
    print_step("Vérification des Translator en soft-delete")
    cmd = "az cognitiveservices account list-deleted --query \"[?kind=='TextTranslation'].{name:name, location:location, deletionDate:deletionDate}\" -o json"
    success, deleted = run_command(cmd, capture=True, check=False)
    
    if success and deleted and deleted.strip() != "[]":
        try:
            import json
            deleted_list = json.loads(deleted)
            if deleted_list:
                print_warning(f"Trouvé {len(deleted_list)} Translator(s) en soft-delete:")
                for idx, item in enumerate(deleted_list, 1):
                    print_info(f"{idx}. {item['name']} (supprimé le {item.get('deletionDate', 'N/A')})")
                
                print_info("\n⚠️  Les Translator F0 soft-deleted bloquent la création de nouveaux F0")
                print_info("Il faut les purger définitivement (irréversible !)")
                
                response = input(f"\n{Colors.BOLD}Voulez-vous purger ces Translator? (o/n): {Colors.END}").lower()
                if response == 'o':
                    for item in deleted_list:
                        print_step(f"Purge de {item['name']}...")
                        cmd = f"az cognitiveservices account purge --name {item['name']} --resource-group {config['resource_group']} --location {item['location']}"
                        run_command(cmd, check=False)
                        print_success(f"Purgé: {item['name']}")
                    
                    print_info("Attente de 30 secondes pour la propagation...")
                    import time
                    time.sleep(30)
        except:
            pass
    
    # 3. Créer le Translator
    print_step(f"Création du service Translator ({sku})")
    cmd = f"""az cognitiveservices account create \
        --name {config['translator_name']} \
        --resource-group {config['resource_group']} \
        --kind TextTranslation \
        --sku {sku} \
        --location global \
        --tags application=translation-service client={config['client_name']} \
        --yes"""
    
    success, output = run_command(cmd, capture=True, check=False)
    if not success:
        if "already exists" in output or "AlreadyExists" in output:
            print_warning("Le Translator existe déjà, tentative de récupération...")
        else:
            print_error(f"Échec de la création du Translator")
            print_info("Vérifiez les limitations F0 et soft-delete")
            return False
    
    config['sku_translator'] = sku
    print_success(f"Translator créé: {config['translator_name']} ({sku})")
    if sku == "S1":
        print_warning("⚠️  SKU S1 utilisé (payant: ~10€/mois)")
    
    # Récupérer la clé et l'endpoint
    cmd = f"az cognitiveservices account keys list --name {config['translator_name']} --resource-group {config['resource_group']} --query 'key1' -o tsv"
    success, translator_key = run_command(cmd, capture=True)
    if not success:
        return False
    
    config['translator_key'] = translator_key
    config['translator_endpoint'] = "https://api.cognitive.microsofttranslator.com"
    
    return True

def create_function_app(config: Dict) -> bool:
    """Crée et configure l'Azure Function App"""
    # Créer le App Service Plan (Basic B1)
    # Note: Y1 (Consumption) n'est pas toujours disponible selon les subscriptions
    cmd = f"""az functionapp plan create \
        --name {config['app_service_plan']} \
        --resource-group {config['resource_group']} \
        --location {config['region']} \
        --sku B1 \
        --is-linux"""
    
    success, _ = run_command(cmd, "Création du App Service Plan")
    if not success:
        return False
    
    print_success(f"App Service Plan créé: {config['app_service_plan']}")
    
    # Créer la Function App
    cmd = f"""az functionapp create \
        --name {config['function_app']} \
        --resource-group {config['resource_group']} \
        --plan {config['app_service_plan']} \
        --storage-account {config['storage_account']} \
        --runtime python \
        --runtime-version 3.12 \
        --functions-version 4 \
        --os-type Linux \
        --tags application=translation-service client={config['client_name']}"""
    
    success, _ = run_command(cmd, "Création de la Function App")
    if not success:
        return False
    
    print_success(f"Function App créée: {config['function_app']}")
    
    config['function_app_url'] = f"https://{config['function_app']}.azurewebsites.net"
    
    return True

def configure_function_app(config: Dict) -> bool:
    """Configure les variables d'environnement de la Function App"""
    print_step("Configuration des variables d'environnement")
    
    settings = [
        f"AZURE_ACCOUNT_NAME={config['storage_account']}",
        f"AZURE_ACCOUNT_KEY={config['storage_key']}",
        f"TRANSLATOR_KEY={config['translator_key']}",
        f"TRANSLATOR_ENDPOINT={config['translator_endpoint']}",
        f"TRANSLATOR_REGION={config['region']}",
        "INPUT_CONTAINER=doc-to-trad",
        "OUTPUT_CONTAINER=doc-trad",
        "CLEANUP_INTERVAL_HOURS=1"
    ]
    
    if config.get('enable_onedrive'):
        settings.extend([
            "ONEDRIVE_UPLOAD_ENABLED=true",
            f"CLIENT_ID={config['onedrive_client_id']}",
            f"SECRET_ID={config['onedrive_client_secret']}",
            f"TENANT_ID={config['onedrive_tenant_id']}",
            f"ONEDRIVE_FOLDER={config['onedrive_folder']}"
        ])
    else:
        settings.append("ONEDRIVE_UPLOAD_ENABLED=false")
    
    settings_str = " ".join(settings)
    cmd = f"az functionapp config appsettings set --name {config['function_app']} --resource-group {config['resource_group']} --settings {settings_str}"
    
    success, _ = run_command(cmd)
    if success:
        print_success("Variables d'environnement configurées")
    
    return success

def deploy_function_code(config: Dict) -> bool:
    """Déploie le code de l'Azure Function"""
    print_step("Déploiement du code de l'Azure Function")
    
    # Vérifier qu'on est dans le bon répertoire
    project_root = Path(__file__).parent
    
    if not (project_root / "host.json").exists():
        print_error("Impossible de trouver le projet Azure Functions")
        return False
    
    cmd = f"func azure functionapp publish {config['function_app']} --python"
    success, _ = run_command(cmd, "Déploiement du code (cela peut prendre quelques minutes)")
    
    if success:
        print_success("Code déployé avec succès")
    
    return success

def get_function_key(config: Dict) -> bool:
    """Récupère la clé de fonction"""
    print_step("Récupération de la clé API")
    
    cmd = f"az functionapp keys list --name {config['function_app']} --resource-group {config['resource_group']} --query 'functionKeys.default' -o tsv"
    success, key = run_command(cmd, capture=True)
    
    if success and key:
        config['function_key'] = key
        print_success("Clé API récupérée")
        return True
    
    print_warning("Impossible de récupérer la clé (elle sera disponible après le premier démarrage)")
    return True

def test_deployment(config: Dict) -> bool:
    """Teste le déploiement"""
    print_header("TEST DU DÉPLOIEMENT")
    
    import time
    import requests
    
    print_info("Attente du démarrage de la Function App (30 secondes)...")
    time.sleep(30)
    
    health_url = f"{config['function_app_url']}/api/health"
    if config.get('function_key'):
        health_url += f"?code={config['function_key']}"
    
    try:
        print_step("Test de l'endpoint /health")
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            print_success("Endpoint /health: OK")
            data = response.json()
            print_info(f"Status: {data.get('status')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                if status == 'connected':
                    print_success(f"  {service}: {status}")
                else:
                    print_error(f"  {service}: {status}")
            
            return True
        else:
            print_error(f"Endpoint /health: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erreur lors du test: {e}")
        return False

def save_deployment_info(config: Dict):
    """Sauvegarde les informations de déploiement"""
    print_step("Sauvegarde des informations de déploiement")
    
    output_file = Path(f"deployment-{config['client_name']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print_success(f"Informations sauvegardées dans: {output_file}")
    
    # Afficher le résumé
    print_header("DÉPLOIEMENT TERMINÉ")
    print_success("Toutes les ressources ont été créées avec succès!")
    print()
    print_info(f"URL de l'API: {config['function_app_url']}")
    if config.get('function_key'):
        print_info(f"Clé API: {config['function_key']}")
    print()
    print_info(f"Resource Group: {config['resource_group']}")
    print_info(f"Storage Account: {config['storage_account']}")
    print_info(f"Translator: {config['translator_name']}")
    print_info(f"Function App: {config['function_app']}")
    print()
    print_warning("IMPORTANT: Notez ces informations pour le déploiement Power Apps")

def deploy_power_platform_solution(config: Dict) -> bool:
    """Déploie la solution Power Platform"""
    print_header("DÉPLOIEMENT POWER PLATFORM")
    
    response = input(f"\n{Colors.BOLD}Voulez-vous déployer la solution Power Apps maintenant? (o/n): {Colors.END}").lower()
    if response != 'o':
        print_info("Vous pouvez déployer la solution plus tard avec le script deploy_power_platform.py")
        return True
    
    # Collecte des informations Power Platform
    print_info("\nConnectez-vous à Power Platform avec les credentials du client")
    
    tenant_id = input(f"{Colors.BOLD}Tenant ID: {Colors.END}").strip()
    environment_url = input(f"{Colors.BOLD}Environment URL (ex: https://xxx.crm4.dynamics.com): {Colors.END}").strip()
    
    solution_path = Path(__file__).parent / "Solution" / "BotCopilotTraducteur_1_0_0_2.zip"
    
    if not solution_path.exists():
        print_error(f"Solution introuvable: {solution_path}")
        return False
    
    # Authentification
    print_step("Authentification Power Platform")
    success, _ = run_command(f"pac auth create --tenant {tenant_id} --url {environment_url}")
    if not success:
        print_error("Échec de l'authentification")
        return False
    
    # Import de la solution
    print_step("Import de la solution (cela peut prendre plusieurs minutes)")
    cmd = f"pac solution import --path {solution_path} --async"
    success, _ = run_command(cmd)
    
    if success:
        print_success("Solution importée avec succès!")
        print_info("\nÉtapes suivantes:")
        print_info("1. Ouvrez Power Apps (https://make.powerapps.com)")
        print_info("2. Configurez le connecteur personnalisé avec:")
        print_info(f"   - URL: {config['function_app_url']}")
        print_info(f"   - Clé: {config.get('function_key', 'À récupérer')}")
        print_info("3. Publiez le bot dans Copilot Studio")
        return True
    else:
        print_error("Échec de l'import de la solution")
        return False

def main():
    """Fonction principale"""
    print_header("DÉPLOIEMENT BOT TRADUCTEUR")
    print_info("VM de déploiement - Configuration client")
    
    # Vérifications préalables
    if not check_prerequisites():
        sys.exit(1)
    
    if not check_azure_login():
        print_error("Connexion Azure requise")
        sys.exit(1)
    
    # Collecte des informations
    config = collect_deployment_info()
    if not config:
        sys.exit(0)
    
    # Déploiement Azure
    print_header("DÉPLOIEMENT DES RESSOURCES AZURE")
    
    steps = [
        ("Resource Group", lambda: create_resource_group(config)),
        ("Storage Account", lambda: create_storage_account(config)),
        ("Azure Translator", lambda: create_translator(config)),
        ("Function App", lambda: create_function_app(config)),
        ("Configuration", lambda: configure_function_app(config)),
        ("Déploiement du code", lambda: deploy_function_code(config)),
        ("Récupération de la clé", lambda: get_function_key(config))
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"\nÉchec lors de l'étape: {step_name}")
            print_info("\nRessources créées:")
            for key in ['resource_group', 'storage_account', 'translator_name', 'function_app']:
                if key in config:
                    print_info(f"  - {key}: {config[key]}")
            print_warning("\nVous pouvez nettoyer les ressources avec:")
            print_info(f"  az group delete --name {config['resource_group']} --yes")
            sys.exit(1)
        print()
    
    # Test
    test_deployment(config)
    
    # Sauvegarde
    save_deployment_info(config)
    
    # Power Platform (optionnel)
    deploy_power_platform_solution(config)
    
    print_header("DÉPLOIEMENT COMPLET")
    print_success("Le client est prêt à utiliser le service de traduction!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Déploiement annulé par l'utilisateur{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nErreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
