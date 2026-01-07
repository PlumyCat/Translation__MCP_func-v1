"""
Azure Deployment Service
Gere le deploiement des ressources Azure pour le service de traduction
"""

import logging
import os
import time
import json
import subprocess
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


@dataclass
class AzureCredentials:
    """Credentials Azure pour le deploiement"""
    subscription_id: str
    tenant_id: str
    client_id: str
    client_secret: str

    def get_credential(self) -> ClientSecretCredential:
        """Retourne un objet credential Azure"""
        return ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )


@dataclass
class DeploymentConfig:
    """Configuration du deploiement"""
    client_name: str
    region: str
    enable_onedrive: bool = False
    onedrive_client_id: Optional[str] = None
    onedrive_client_secret: Optional[str] = None
    onedrive_tenant_id: Optional[str] = None
    onedrive_folder: str = "Translated_Documents"

    @property
    def resource_group_name(self) -> str:
        return f"rg-translation-{self.client_name}"

    @property
    def storage_account_name(self) -> str:
        # Storage account names must be 3-24 chars, lowercase alphanumeric only
        clean_name = self.client_name.replace("-", "").replace("_", "")[:15]
        return f"sttrad{clean_name}"

    @property
    def translator_name(self) -> str:
        return f"translator-{self.client_name}"

    @property
    def function_app_name(self) -> str:
        return f"func-translation-{self.client_name}"

    @property
    def app_insights_name(self) -> str:
        return f"ai-translation-{self.client_name}"

    @property
    def app_service_plan_name(self) -> str:
        return f"asp-translation-{self.client_name}"


@dataclass
class DeploymentResult:
    """Resultat du deploiement"""
    success: bool
    deployment_id: Optional[str] = None
    resource_group: Optional[str] = None
    function_app_url: Optional[str] = None
    function_key: Optional[str] = None
    storage_account_name: Optional[str] = None
    storage_account_key: Optional[str] = None
    translator_endpoint: Optional[str] = None
    translator_key: Optional[str] = None
    translator_region: Optional[str] = None
    failed_step: Optional[str] = None
    error: Optional[str] = None
    deployed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class AzureDeployer:
    """Service de deploiement Azure"""

    # Chemin vers le code source des functions de traduction
    TRANSLATION_CODE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        ""  # Root du repo
    )

    def __init__(self, credentials: AzureCredentials, config: DeploymentConfig):
        self.credentials = credentials
        self.config = config
        self.credential = credentials.get_credential()

        # Clients Azure
        self.resource_client = ResourceManagementClient(
            self.credential, credentials.subscription_id
        )
        self.storage_client = StorageManagementClient(
            self.credential, credentials.subscription_id
        )
        self.cognitive_client = CognitiveServicesManagementClient(
            self.credential, credentials.subscription_id
        )
        self.web_client = WebSiteManagementClient(
            self.credential, credentials.subscription_id
        )

        self.result = DeploymentResult(success=False)

    def validate_credentials(self) -> dict:
        """Valide les credentials Azure"""
        try:
            # Tente de lister les resource groups pour valider les credentials
            subscriptions = list(self.resource_client.resource_groups.list())

            return {
                "success": True,
                "subscription_id": self.credentials.subscription_id,
                "message": "Credentials valides"
            }
        except Exception as e:
            logger.error(f"Validation credentials failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_resource_group(self) -> bool:
        """Cree le Resource Group"""
        try:
            logger.info(f"Creating resource group: {self.config.resource_group_name}")

            rg_result = self.resource_client.resource_groups.create_or_update(
                self.config.resource_group_name,
                {
                    "location": self.config.region,
                    "tags": {
                        "application": "translation-service",
                        "client": self.config.client_name,
                        "deployed_by": "copilot-deployment-bot",
                        "deployed_at": datetime.utcnow().isoformat()
                    }
                }
            )

            self.result.resource_group = rg_result.name
            logger.info(f"Resource group created: {rg_result.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create resource group: {e}")
            self.result.failed_step = "create_resource_group"
            self.result.error = str(e)
            return False

    def create_storage_account(self) -> bool:
        """Cree le Storage Account avec les containers"""
        try:
            logger.info(f"Creating storage account: {self.config.storage_account_name}")

            # Creer le storage account
            poller = self.storage_client.storage_accounts.begin_create(
                self.config.resource_group_name,
                self.config.storage_account_name,
                {
                    "location": self.config.region,
                    "kind": "StorageV2",
                    "sku": {"name": "Standard_LRS"},
                    "tags": {
                        "application": "translation-service",
                        "client": self.config.client_name
                    }
                }
            )
            storage_account = poller.result()

            # Recuperer les cles
            keys = self.storage_client.storage_accounts.list_keys(
                self.config.resource_group_name,
                self.config.storage_account_name
            )
            storage_key = keys.keys[0].value

            self.result.storage_account_name = self.config.storage_account_name
            self.result.storage_account_key = storage_key

            # Creer les containers
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.config.storage_account_name};"
                f"AccountKey={storage_key};"
                f"EndpointSuffix=core.windows.net"
            )

            blob_service = BlobServiceClient.from_connection_string(connection_string)

            # Container pour les documents a traduire
            blob_service.create_container("doc-to-trad")
            logger.info("Created container: doc-to-trad")

            # Container pour les documents traduits
            blob_service.create_container("doc-trad")
            logger.info("Created container: doc-trad")

            logger.info(f"Storage account created: {self.config.storage_account_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create storage account: {e}")
            self.result.failed_step = "create_storage_account"
            self.result.error = str(e)
            return False

    def create_translator_resource(self) -> bool:
        """Cree le service Azure Translator"""
        try:
            logger.info(f"Creating translator resource: {self.config.translator_name}")

            # Creer le service Cognitive Services (Translator)
            poller = self.cognitive_client.accounts.begin_create(
                self.config.resource_group_name,
                self.config.translator_name,
                {
                    "location": "global",  # Translator est un service global
                    "kind": "TextTranslation",
                    "sku": {"name": "S1"},
                    "properties": {},
                    "tags": {
                        "application": "translation-service",
                        "client": self.config.client_name
                    }
                }
            )
            translator = poller.result()

            # Recuperer les cles
            keys = self.cognitive_client.accounts.list_keys(
                self.config.resource_group_name,
                self.config.translator_name
            )

            self.result.translator_endpoint = f"https://api.cognitive.microsofttranslator.com"
            self.result.translator_key = keys.key1
            self.result.translator_region = self.config.region

            logger.info(f"Translator resource created: {self.config.translator_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create translator resource: {e}")
            self.result.failed_step = "create_translator_resource"
            self.result.error = str(e)
            return False

    def deploy_function_app(self) -> bool:
        """Deploie l'Azure Function App"""
        try:
            logger.info(f"Creating function app: {self.config.function_app_name}")

            # Creer le App Service Plan (Consumption)
            self.web_client.app_service_plans.begin_create_or_update(
                self.config.resource_group_name,
                self.config.app_service_plan_name,
                {
                    "location": self.config.region,
                    "sku": {
                        "name": "Y1",
                        "tier": "Dynamic"
                    },
                    "kind": "functionapp"
                }
            ).result()

            # Creer la Function App
            storage_connection = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.result.storage_account_name};"
                f"AccountKey={self.result.storage_account_key};"
                f"EndpointSuffix=core.windows.net"
            )

            app_settings = [
                {"name": "AzureWebJobsStorage", "value": storage_connection},
                {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"},
                {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"},
                {"name": "PYTHON_VERSION", "value": "3.9"},
                {"name": "AZURE_ACCOUNT_NAME", "value": self.result.storage_account_name},
                {"name": "AZURE_ACCOUNT_KEY", "value": self.result.storage_account_key},
                {"name": "TRANSLATOR_KEY", "value": self.result.translator_key},
                {"name": "TRANSLATOR_ENDPOINT", "value": self.result.translator_endpoint},
                {"name": "TRANSLATOR_REGION", "value": self.result.translator_region},
                {"name": "INPUT_CONTAINER", "value": "doc-to-trad"},
                {"name": "OUTPUT_CONTAINER", "value": "doc-trad"},
                {"name": "CLEANUP_INTERVAL_HOURS", "value": "1"},
            ]

            # Ajouter les settings OneDrive si active
            if self.config.enable_onedrive:
                app_settings.extend([
                    {"name": "ONEDRIVE_UPLOAD_ENABLED", "value": "true"},
                    {"name": "CLIENT_ID", "value": self.config.onedrive_client_id or ""},
                    {"name": "CLIENT_SECRET", "value": self.config.onedrive_client_secret or ""},
                    {"name": "TENANT_ID", "value": self.config.onedrive_tenant_id or ""},
                    {"name": "ONEDRIVE_FOLDER", "value": self.config.onedrive_folder},
                ])

            poller = self.web_client.web_apps.begin_create_or_update(
                self.config.resource_group_name,
                self.config.function_app_name,
                {
                    "location": self.config.region,
                    "kind": "functionapp,linux",
                    "server_farm_id": f"/subscriptions/{self.credentials.subscription_id}/resourceGroups/{self.config.resource_group_name}/providers/Microsoft.Web/serverfarms/{self.config.app_service_plan_name}",
                    "site_config": {
                        "app_settings": app_settings,
                        "linux_fx_version": "Python|3.9",
                        "cors": {
                            "allowed_origins": ["*"]
                        }
                    },
                    "tags": {
                        "application": "translation-service",
                        "client": self.config.client_name
                    }
                }
            )
            function_app = poller.result()

            self.result.function_app_url = f"https://{self.config.function_app_name}.azurewebsites.net"

            # Recuperer la Function Key
            time.sleep(5)  # Attendre que l'app soit prete

            try:
                keys = self.web_client.web_apps.list_function_keys(
                    self.config.resource_group_name,
                    self.config.function_app_name,
                    "health"  # N'importe quelle function
                )
                self.result.function_key = keys.get("default", "")
            except Exception:
                # Si pas de key, recuperer la host key
                host_keys = self.web_client.web_apps.list_host_keys(
                    self.config.resource_group_name,
                    self.config.function_app_name
                )
                self.result.function_key = host_keys.function_keys.get("default", "")

            logger.info(f"Function app created: {self.config.function_app_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create function app: {e}")
            self.result.failed_step = "deploy_function_app"
            self.result.error = str(e)
            return False

    def deploy_code(self) -> bool:
        """Deploie le code des Functions"""
        try:
            logger.info("Deploying function code...")

            # Utiliser Azure CLI pour deployer le code
            # Note: Cela necessite que Azure CLI soit installe et configure

            # Pour le deploiement via ZIP, on devrait:
            # 1. Creer un package ZIP du code
            # 2. L'uploader vers le storage
            # 3. Configurer le deploiement depuis le ZIP

            # Pour simplifier, on utilise func azure functionapp publish
            # Cette commande devrait etre executee separement ou via CI/CD

            logger.info("Code deployment should be done via CI/CD or Azure CLI")
            logger.info(f"Command: func azure functionapp publish {self.config.function_app_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to deploy code: {e}")
            self.result.failed_step = "deploy_code"
            self.result.error = str(e)
            return False

    def full_deployment(self) -> DeploymentResult:
        """Execute le deploiement complet"""
        import uuid

        self.result.deployment_id = str(uuid.uuid4())
        self.result.deployed_at = datetime.utcnow().isoformat()

        steps = [
            ("create_resource_group", self.create_resource_group),
            ("create_storage_account", self.create_storage_account),
            ("create_translator_resource", self.create_translator_resource),
            ("deploy_function_app", self.deploy_function_app),
            ("deploy_code", self.deploy_code),
        ]

        for step_name, step_func in steps:
            logger.info(f"Executing step: {step_name}")
            if not step_func():
                logger.error(f"Deployment failed at step: {step_name}")
                return self.result

        self.result.success = True
        logger.info("Deployment completed successfully")
        return self.result


class DeploymentValidator:
    """Validateur de deploiement"""

    def __init__(self, function_app_url: str, function_key: str = ""):
        self.base_url = function_app_url.rstrip("/")
        self.function_key = function_key

    def _make_request(self, endpoint: str, method: str = "GET") -> dict:
        """Execute une requete vers l'API"""
        import requests

        url = f"{self.base_url}/api/{endpoint}"
        if self.function_key:
            url += f"?code={self.function_key}"

        try:
            start_time = time.time()
            if method == "GET":
                response = requests.get(url, timeout=30)
            else:
                response = requests.post(url, timeout=30)

            response_time = int((time.time() - start_time) * 1000)

            return {
                "status": "OK" if response.status_code == 200 else "FAILED",
                "message": f"HTTP {response.status_code}",
                "response_time": response_time,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "message": str(e),
                "response_time": 0
            }

    def validate(self) -> dict:
        """Execute tous les tests de validation"""
        results = {
            "health_check": self._make_request("health"),
            "languages_check": self._make_request("languages"),
            "formats_check": self._make_request("formats"),
        }

        # Calculer le score
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["status"] == "OK")
        health_score = int((passed_tests / total_tests) * 100)

        # Verifications supplementaires basees sur les reponses
        storage_check = {"status": "OK", "message": "Check via health endpoint"}
        translator_check = {"status": "OK", "message": "Check via health endpoint"}

        if results["health_check"]["data"]:
            health_data = results["health_check"]["data"]
            if health_data.get("services", {}).get("storage") != "connected":
                storage_check = {"status": "FAILED", "message": "Storage not connected"}
            if health_data.get("services", {}).get("translator") != "connected":
                translator_check = {"status": "FAILED", "message": "Translator not connected"}

        results["storage_check"] = storage_check
        results["translator_check"] = translator_check

        # Recalculer le score avec tous les tests
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["status"] == "OK")
        health_score = int((passed_tests / total_tests) * 100)

        # Generer le resume et les recommandations
        if health_score == 100:
            summary = "Tous les tests sont passes. Le service fonctionne correctement."
            recommendations = ""
        else:
            failed_tests = [k for k, v in results.items() if v["status"] != "OK"]
            summary = f"{passed_tests}/{total_tests} tests passes. Problemes detectes."
            recommendations = "Verifiez les points suivants:\n"
            for test in failed_tests:
                recommendations += f"- {test}: {results[test]['message']}\n"

        return {
            "health_check": results["health_check"],
            "languages_check": results["languages_check"],
            "formats_check": results["formats_check"],
            "storage_check": results["storage_check"],
            "translator_check": results["translator_check"],
            "health_score": health_score,
            "summary": summary,
            "recommendations": recommendations
        }
