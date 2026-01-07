"""
Power Platform Service
Gere les operations Power Platform via pac CLI
"""

import logging
import subprocess
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional, List

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
    """Service pour interagir avec Power Platform via pac CLI"""

    def __init__(self, credentials: PowerPlatformCredentials):
        self.credentials = credentials
        self._pac_path = self._find_pac()

    def _find_pac(self) -> str:
        """Trouve le chemin vers pac CLI"""
        # Essayer plusieurs emplacements possibles
        possible_paths = [
            "pac",  # Dans le PATH
            "/usr/local/bin/pac",
            os.path.expanduser("~/.dotnet/tools/pac"),
            "C:\\Program Files\\Microsoft Power Platform CLI\\pac.exe",
        ]

        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        raise RuntimeError("pac CLI n'est pas installe ou n'est pas dans le PATH")

    def _run_pac(self, args: List[str], timeout: int = 300) -> subprocess.CompletedProcess:
        """Execute une commande pac"""
        cmd = [self._pac_path] + args
        logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout apres {timeout} secondes")

    def _authenticate(self, environment_url: Optional[str] = None, admin: bool = False) -> bool:
        """Authentification au tenant"""
        # Clear existing auth
        self._run_pac(["auth", "clear"])

        # Build auth command
        auth_args = [
            "auth", "create",
            "--tenant", self.credentials.tenant_id,
            "--applicationId", self.credentials.client_id,
            "--clientSecret", self.credentials.client_secret
        ]

        if admin:
            auth_args.extend(["--kind", "admin"])
        elif environment_url:
            auth_args.extend(["--environment", environment_url])

        result = self._run_pac(auth_args)

        if result.returncode != 0:
            logger.error(f"Auth failed: {result.stderr}")
            return False

        return True

    def list_environments(self) -> List[EnvironmentInfo]:
        """Liste les environnements Power Platform"""
        if not self._authenticate(admin=True):
            raise RuntimeError("Echec de l'authentification admin")

        result = self._run_pac(["admin", "list", "--json"])

        if result.returncode != 0:
            raise RuntimeError(f"Echec de la liste: {result.stderr}")

        environments = json.loads(result.stdout)

        return [
            EnvironmentInfo(
                environment_id=env.get("EnvironmentId", ""),
                display_name=env.get("DisplayName", ""),
                url=env.get("Url", ""),
                dataverse_enabled=bool(env.get("Url")),
                region=env.get("Region", ""),
                state=env.get("State", "")
            )
            for env in environments
        ]

    def check_dataverse(self, environment_id_or_name: str) -> DataverseCheckResult:
        """Verifie si Dataverse est active dans un environnement"""
        result = DataverseCheckResult(success=False, dataverse_enabled=False)

        try:
            # Authentification admin pour lister les environnements
            if not self._authenticate(admin=True):
                result.error = "Echec de l'authentification admin"
                return result

            # Lister les environnements
            list_result = self._run_pac(["admin", "list", "--json"])

            if list_result.returncode != 0:
                result.error = f"Impossible de lister les environnements: {list_result.stderr}"
                return result

            environments = json.loads(list_result.stdout)

            # Trouver l'environnement
            target_env = None
            for env in environments:
                if (env.get("EnvironmentId") == environment_id_or_name or
                    env.get("DisplayName") == environment_id_or_name):
                    target_env = env
                    break

            if not target_env:
                result.error = f"Environnement non trouve: {environment_id_or_name}"
                return result

            result.environment_name = target_env.get("DisplayName", "")
            result.environment_url = target_env.get("Url", "")

            # Verifier si Dataverse est active (presence d'une URL)
            if result.environment_url and ".dynamics.com" in result.environment_url:
                result.dataverse_enabled = True

                # Se connecter pour plus de details
                if self._authenticate(environment_url=result.environment_url):
                    who_result = self._run_pac(["org", "who", "--json"])
                    if who_result.returncode == 0:
                        org_data = json.loads(who_result.stdout)
                        result.organization_id = org_data.get("OrganizationId", "")

            result.success = True

        except Exception as e:
            result.error = str(e)
            logger.error(f"check_dataverse error: {e}")

        return result

    def enable_dataverse(
        self,
        environment_name: str,
        region: str = "france",
        environment_type: str = "Production",
        currency: str = "EUR",
        language: int = 1036
    ) -> DataverseEnableResult:
        """Cree un nouvel environnement avec Dataverse"""
        result = DataverseEnableResult(success=False)

        try:
            # Authentification admin
            if not self._authenticate(admin=True):
                result.error = "Echec de l'authentification admin"
                return result

            # Generer un nom de domaine unique
            import re
            import random
            domain_name = re.sub(r'[^a-zA-Z0-9]', '', environment_name).lower()[:20]
            domain_name = f"{domain_name}{random.randint(100, 999)}"

            logger.info(f"Creating environment: {environment_name}, domain: {domain_name}")

            # Creer l'environnement
            create_result = self._run_pac([
                "admin", "create",
                "--name", environment_name,
                "--type", environment_type,
                "--region", region,
                "--currency", currency,
                "--language", str(language),
                "--domain", domain_name
            ], timeout=600)

            if create_result.returncode != 0:
                result.error = f"Echec de la creation: {create_result.stderr}"
                return result

            # Attendre que l'environnement soit pret
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(10)
                logger.info(f"Waiting for environment... attempt {attempt + 1}/{max_attempts}")

                list_result = self._run_pac(["admin", "list", "--json"])
                if list_result.returncode == 0:
                    environments = json.loads(list_result.stdout)
                    new_env = next(
                        (e for e in environments if e.get("DisplayName") == environment_name),
                        None
                    )

                    if new_env and new_env.get("Url"):
                        result.environment_id = new_env.get("EnvironmentId", "")
                        result.environment_name = new_env.get("DisplayName", "")
                        result.environment_url = new_env.get("Url", "")
                        result.dataverse_enabled = True
                        result.success = True
                        return result

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
        """Importe une solution dans un environnement Dataverse"""
        result = SolutionImportResult(success=False)

        try:
            # Verifier que le fichier existe
            if not os.path.exists(solution_path):
                result.error = f"Fichier solution non trouve: {solution_path}"
                return result

            # Authentification
            if not self._authenticate(environment_url=environment_url):
                result.error = "Echec de l'authentification"
                return result

            # Verifier la connexion Dataverse
            who_result = self._run_pac(["org", "who", "--json"])
            if who_result.returncode != 0:
                result.error = "Impossible de se connecter a Dataverse"
                return result

            # Construire la commande d'import
            import_args = [
                "solution", "import",
                "--path", solution_path,
                "--activate-plugins"
            ]

            if overwrite:
                import_args.append("--force-overwrite")

            # Executer l'import
            import_result = self._run_pac(import_args, timeout=600)

            if import_result.returncode != 0:
                error_msg = import_result.stderr or import_result.stdout

                if "same version already exists" in error_msg:
                    result.error = "La solution existe deja avec la meme version"
                elif "Missing dependencies" in error_msg:
                    result.error = "Dependances manquantes"
                else:
                    result.error = f"Echec de l'import: {error_msg}"
                return result

            # Parser le resultat
            import re
            output = import_result.stdout

            name_match = re.search(r"Solution (.+) imported", output)
            if name_match:
                result.solution_name = name_match.group(1)

            version_match = re.search(r"Version: (.+)", output)
            if version_match:
                result.solution_version = version_match.group(1)

            result.success = True

        except Exception as e:
            result.error = str(e)
            logger.error(f"import_solution error: {e}")

        return result
