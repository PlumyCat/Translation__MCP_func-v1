"""
Power Platform Service - Version API REST
Gere les operations Power Platform via les APIs REST (sans pac CLI)
"""

import logging
import time
import base64
import os
from dataclasses import dataclass, asdict
from typing import Optional, List
import requests

logger = logging.getLogger(__name__)


@dataclass
class PowerPlatformCredentials:
    """Credentials Power Platform"""
    tenant_id: str
    client_id: str
    client_secret: str


@dataclass
class EnvironmentInfo:
    """Informations sur un environnement Power Platform"""
    environment_id: str
    display_name: str
    url: str
    dataverse_enabled: bool
    region: str
    state: str


@dataclass
class DataverseCheckResult:
    """Resultat de la verification Dataverse"""
    success: bool
    dataverse_enabled: bool
    environment_name: str = ""
    environment_url: str = ""
    organization_id: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DataverseEnableResult:
    """Resultat de l'activation Dataverse"""
    success: bool
    environment_id: str = ""
    environment_name: str = ""
    environment_url: str = ""
    dataverse_enabled: bool = False
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SolutionImportResult:
    """Resultat de l'import de solution"""
    success: bool
    solution_name: str = ""
    solution_version: str = ""
    import_job_id: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class PowerPlatformService:
    """Service pour interagir avec Power Platform via APIs REST"""

    # URLs des APIs
    BAP_API_URL = "https://api.bap.microsoft.com"
    LOGIN_URL = "https://login.microsoftonline.com"

    # Scopes pour les differentes APIs
    BAP_SCOPE = "https://api.bap.microsoft.com/.default"

    def __init__(self, credentials: PowerPlatformCredentials):
        self.credentials = credentials
        self._tokens = {}  # Cache des tokens

    def _get_token(self, scope: str) -> str:
        """Obtient un token d'acces pour le scope specifie"""
        # Verifier le cache
        if scope in self._tokens:
            token_data = self._tokens[scope]
            # Verifier si le token est encore valide (avec marge de 5 min)
            if token_data.get("expires_at", 0) > time.time() + 300:
                return token_data["access_token"]

        # Obtenir un nouveau token
        token_url = f"{self.LOGIN_URL}/{self.credentials.tenant_id}/oauth2/v2.0/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scope": scope
        }

        logger.info(f"Getting token for scope: {scope}")

        response = requests.post(token_url, data=data, timeout=30)

        if response.status_code != 200:
            error_detail = response.json().get("error_description", response.text)
            raise RuntimeError(f"Failed to get token: {error_detail}")

        token_data = response.json()
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)

        # Mettre en cache
        self._tokens[scope] = token_data

        return token_data["access_token"]

    def _get_bap_token(self) -> str:
        """Obtient un token pour l'API BAP (Power Platform Admin)"""
        return self._get_token(self.BAP_SCOPE)

    def _get_dataverse_token(self, org_url: str) -> str:
        """Obtient un token pour l'API Dataverse"""
        # Extraire le host de l'URL
        org_host = org_url.replace("https://", "").replace("http://", "").rstrip("/")
        scope = f"https://{org_host}/.default"
        return self._get_token(scope)

    def list_environments(self) -> List[EnvironmentInfo]:
        """Liste les environnements Power Platform"""
        token = self._get_bap_token()

        url = f"{self.BAP_API_URL}/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments"
        params = {"api-version": "2023-06-01"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        logger.info("Listing Power Platform environments")

        response = requests.get(url, headers=headers, params=params, timeout=60)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to list environments: {response.status_code} - {response.text}")

        data = response.json()
        environments = []

        for env in data.get("value", []):
            properties = env.get("properties", {})
            linked_env = properties.get("linkedEnvironmentMetadata", {})

            env_info = EnvironmentInfo(
                environment_id=env.get("name", ""),
                display_name=properties.get("displayName", ""),
                url=linked_env.get("instanceUrl", ""),
                dataverse_enabled=bool(linked_env.get("instanceUrl")),
                region=properties.get("azureRegion", ""),
                state=properties.get("states", {}).get("management", {}).get("id", "")
            )
            environments.append(env_info)

        return environments

    def check_dataverse(self, environment_id_or_name: str) -> DataverseCheckResult:
        """Verifie si Dataverse est active dans un environnement"""
        result = DataverseCheckResult(success=False, dataverse_enabled=False)

        try:
            environments = self.list_environments()

            # Chercher l'environnement par ID ou nom (recherche flexible)
            target_env = None
            search_lower = environment_id_or_name.lower()

            for env in environments:
                # Match exact ou partiel
                if (env.environment_id.lower() == search_lower or
                    env.display_name.lower() == search_lower or
                    search_lower in env.display_name.lower() or
                    search_lower in env.environment_id.lower()):
                    target_env = env
                    break

            if not target_env:
                # Lister les environnements disponibles pour aider
                available = [f"'{e.display_name}' (ID: {e.environment_id})" for e in environments[:5]]
                result.error = f"Environnement non trouve: '{environment_id_or_name}'. Disponibles: {', '.join(available)}"
                return result

            result.environment_name = target_env.display_name
            result.environment_url = target_env.url
            result.dataverse_enabled = target_env.dataverse_enabled

            if target_env.dataverse_enabled and target_env.url:
                # Essayer de recuperer plus d'infos via l'API Dataverse
                try:
                    token = self._get_dataverse_token(target_env.url)
                    org_url = f"{target_env.url.rstrip('/')}/api/data/v9.2/WhoAmI"

                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }

                    who_response = requests.get(org_url, headers=headers, timeout=30)
                    if who_response.status_code == 200:
                        who_data = who_response.json()
                        result.organization_id = who_data.get("OrganizationId", "")
                except Exception as e:
                    logger.warning(f"Could not get org details: {e}")

            result.success = True

        except Exception as e:
            result.error = str(e)
            logger.error(f"check_dataverse error: {e}")

        return result

    def enable_dataverse(
        self,
        environment_name: str,
        region: str = "france",
        environment_type: str = "Sandbox",
        currency: str = "EUR",
        language: int = 1036
    ) -> DataverseEnableResult:
        """Cree un nouvel environnement avec Dataverse"""
        result = DataverseEnableResult(success=False)

        try:
            token = self._get_bap_token()

            # Mapper les regions aux codes Power Platform
            region_mapping = {
                "france": "france",
                "europe": "europe",
                "unitedstates": "unitedstates",
                "asia": "asia",
                "australia": "australia",
                "canada": "canada",
                "japan": "japan",
                "india": "india",
                "unitedkingdom": "unitedkingdom",
                "southamerica": "southamerica",
                "germany": "germany",
                "switzerland": "switzerland"
            }

            pp_region = region_mapping.get(region.lower(), "europe")

            # Mapper les types d'environnement
            type_mapping = {
                "sandbox": "Sandbox",
                "production": "Production",
                "developer": "Developer"
            }

            pp_type = type_mapping.get(environment_type.lower(), "Sandbox")

            url = f"{self.BAP_API_URL}/providers/Microsoft.BusinessAppPlatform/environments"
            params = {"api-version": "2023-06-01"}

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Generer un nom de domaine unique
            import re
            import random
            domain_name = re.sub(r'[^a-zA-Z0-9]', '', environment_name).lower()[:20]
            domain_name = f"{domain_name}{random.randint(100, 999)}"

            # Corps de la requete pour creer l'environnement
            body = {
                "properties": {
                    "displayName": environment_name,
                    "environmentSku": pp_type,
                    "linkedEnvironmentMetadata": {
                        "baseLanguage": language,
                        "currency": {
                            "code": currency
                        },
                        "domainName": domain_name
                    }
                },
                "location": pp_region
            }

            logger.info(f"Creating environment: {environment_name} in {pp_region}")

            response = requests.post(url, headers=headers, params=params, json=body, timeout=120)

            if response.status_code not in [200, 201, 202]:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", response.text)
                except:
                    pass
                result.error = f"Failed to create environment: {error_msg}"
                return result

            # L'environnement est en cours de creation
            env_data = response.json()
            env_id = env_data.get("name", "")

            logger.info(f"Environment creation initiated: {env_id}")

            # Attendre que l'environnement soit pret (polling)
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(10)
                logger.info(f"Waiting for environment... attempt {attempt + 1}/{max_attempts}")

                try:
                    environments = self.list_environments()
                    new_env = next(
                        (e for e in environments if e.environment_id == env_id or
                         e.display_name.lower() == environment_name.lower()),
                        None
                    )

                    if new_env and new_env.url:
                        result.environment_id = new_env.environment_id
                        result.environment_name = new_env.display_name
                        result.environment_url = new_env.url
                        result.dataverse_enabled = True
                        result.success = True
                        return result
                except Exception as e:
                    logger.warning(f"Error checking environment status: {e}")

            result.error = "Timeout: l'environnement n'est pas pret apres 5 minutes"

        except Exception as e:
            result.error = str(e)
            logger.error(f"enable_dataverse error: {e}")

        return result

    def import_solution(
        self,
        environment_url: str,
        solution_path: str,
        overwrite: bool = True
    ) -> SolutionImportResult:
        """Importe une solution dans un environnement Dataverse depuis un fichier"""
        result = SolutionImportResult(success=False)

        try:
            # Verifier que le fichier existe
            if not os.path.exists(solution_path):
                result.error = f"Fichier solution non trouve: {solution_path}"
                return result

            # Lire le fichier solution
            with open(solution_path, "rb") as f:
                solution_data = f.read()

            return self._import_solution_data(environment_url, solution_data, overwrite)

        except Exception as e:
            result.error = str(e)
            logger.error(f"import_solution error: {e}")
            return result

    def _import_solution_data(
        self,
        environment_url: str,
        solution_data: bytes,
        overwrite: bool = True
    ) -> SolutionImportResult:
        """Importe une solution dans un environnement Dataverse"""
        result = SolutionImportResult(success=False)

        try:
            token = self._get_dataverse_token(environment_url)

            # Encoder la solution en base64
            solution_base64 = base64.b64encode(solution_data).decode("utf-8")

            # URL pour l'import de solution
            import_url = f"{environment_url.rstrip('/')}/api/data/v9.2/ImportSolution"

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0"
            }

            body = {
                "OverwriteUnmanagedCustomizations": overwrite,
                "PublishWorkflows": True,
                "CustomizationFile": solution_base64
            }

            logger.info(f"Importing solution to {environment_url}")

            response = requests.post(import_url, headers=headers, json=body, timeout=600)

            if response.status_code not in [200, 204]:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", response.text)
                except:
                    pass
                result.error = f"Failed to import solution: {error_msg}"
                return result

            result.success = True
            result.solution_name = "Solution importee"

        except Exception as e:
            result.error = str(e)
            logger.error(f"_import_solution_data error: {e}")

        return result
