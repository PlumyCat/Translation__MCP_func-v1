"""
Bootstrap Service - Cree le Service Principal et assigne les roles
Utilise Microsoft Graph API et Azure Management API
"""
import logging
import requests
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class BootstrapService:
    """Service pour creer automatiquement un Service Principal chez le client"""

    GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
    ARM_API_URL = "https://management.azure.com"

    def __init__(
        self,
        tenant_id: str,
        subscription_id: str,
        admin_username: Optional[str] = None,
        admin_password: Optional[str] = None,
        admin_client_id: Optional[str] = None,
        admin_client_secret: Optional[str] = None
    ):
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.admin_client_id = admin_client_id
        self.admin_client_secret = admin_client_secret

    def _get_token(self, scope: str) -> str:
        """Obtient un token d'acces pour le scope specifie"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        if self.admin_client_id and self.admin_client_secret:
            # Client credentials flow (Service Principal admin)
            data = {
                "grant_type": "client_credentials",
                "client_id": self.admin_client_id,
                "client_secret": self.admin_client_secret,
                "scope": scope
            }
        elif self.admin_username and self.admin_password:
            # Resource Owner Password Credentials (ROPC) flow
            # Note: Necessite que l'app soit configuree pour ROPC et pas de MFA
            # Pour un vrai scenario de prod, utiliser device code flow ou interactive
            data = {
                "grant_type": "password",
                "client_id": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",  # Azure CLI client ID
                "username": self.admin_username,
                "password": self.admin_password,
                "scope": scope
            }
        else:
            raise ValueError("No valid credentials provided")

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            error_detail = response.json().get('error_description', response.text)
            raise Exception(f"Failed to get token: {error_detail}")

        return response.json()["access_token"]

    def _get_graph_token(self) -> str:
        """Token pour Microsoft Graph API"""
        return self._get_token("https://graph.microsoft.com/.default")

    def _get_arm_token(self) -> str:
        """Token pour Azure Resource Manager API"""
        return self._get_token("https://management.azure.com/.default")

    def create_app_registration(self, app_name: str) -> Dict[str, Any]:
        """Cree une App Registration dans Entra ID"""
        logging.info(f"Creating app registration: {app_name}")

        token = self._get_graph_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Creer l'application
        app_data = {
            "displayName": app_name,
            "signInAudience": "AzureADMyOrg",
            "requiredResourceAccess": []
        }

        response = requests.post(
            f"{self.GRAPH_API_URL}/applications",
            headers=headers,
            json=app_data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create app: {response.status_code} - {response.text}")

        app = response.json()
        app_id = app["appId"]
        object_id = app["id"]

        logging.info(f"App created: {app_id}")

        return {
            "appId": app_id,
            "objectId": object_id,
            "displayName": app_name
        }

    def create_client_secret(self, app_object_id: str) -> Dict[str, str]:
        """Cree un client secret pour l'application"""
        logging.info(f"Creating client secret for app: {app_object_id}")

        token = self._get_graph_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Secret valide 2 ans
        end_date = (datetime.utcnow() + timedelta(days=730)).isoformat() + "Z"

        secret_data = {
            "passwordCredential": {
                "displayName": "Deployment-Secret",
                "endDateTime": end_date
            }
        }

        response = requests.post(
            f"{self.GRAPH_API_URL}/applications/{app_object_id}/addPassword",
            headers=headers,
            json=secret_data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create secret: {response.status_code} - {response.text}")

        secret = response.json()
        logging.info("Client secret created")

        return {
            "secretId": secret.get("keyId", ""),
            "secretValue": secret["secretText"],
            "expiresAt": end_date
        }

    def create_service_principal(self, app_id: str) -> Dict[str, str]:
        """Cree le Service Principal pour l'application"""
        logging.info(f"Creating service principal for app: {app_id}")

        token = self._get_graph_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        sp_data = {
            "appId": app_id
        }

        response = requests.post(
            f"{self.GRAPH_API_URL}/servicePrincipals",
            headers=headers,
            json=sp_data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create SP: {response.status_code} - {response.text}")

        sp = response.json()
        logging.info(f"Service principal created: {sp['id']}")

        return {
            "servicePrincipalId": sp["id"],
            "appId": sp["appId"]
        }

    def assign_contributor_role(self, service_principal_id: str) -> bool:
        """Assigne le role Contributor sur la subscription"""
        logging.info(f"Assigning Contributor role to SP: {service_principal_id}")

        token = self._get_arm_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Role ID pour Contributor
        contributor_role_id = "b24988ac-6180-42a0-ab88-20f7382dd24c"
        role_assignment_id = str(uuid.uuid4())

        scope = f"/subscriptions/{self.subscription_id}"
        url = f"{self.ARM_API_URL}{scope}/providers/Microsoft.Authorization/roleAssignments/{role_assignment_id}?api-version=2022-04-01"

        role_data = {
            "properties": {
                "roleDefinitionId": f"{scope}/providers/Microsoft.Authorization/roleDefinitions/{contributor_role_id}",
                "principalId": service_principal_id,
                "principalType": "ServicePrincipal"
            }
        }

        response = requests.put(url, headers=headers, json=role_data)

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to assign role: {response.status_code} - {response.text}")

        logging.info("Contributor role assigned")
        return True

    def bootstrap_client(self, app_name: str) -> Dict[str, Any]:
        """
        Execute le bootstrap complet :
        1. Cree l'App Registration
        2. Cree le Service Principal
        3. Cree le Client Secret
        4. Assigne le role Contributor
        """
        try:
            # 1. Creer l'App Registration
            app = self.create_app_registration(app_name)

            # 2. Creer le Service Principal
            sp = self.create_service_principal(app["appId"])

            # 3. Creer le Client Secret
            secret = self.create_client_secret(app["objectId"])

            # 4. Assigner le role Contributor
            self.assign_contributor_role(sp["servicePrincipalId"])

            return {
                "success": True,
                "message": "Service Principal cree avec succes",
                "credentials": {
                    "tenantId": self.tenant_id,
                    "subscriptionId": self.subscription_id,
                    "clientId": app["appId"],
                    "clientSecret": secret["secretValue"],
                    "secretExpiresAt": secret["expiresAt"]
                },
                "details": {
                    "appName": app["displayName"],
                    "appObjectId": app["objectId"],
                    "servicePrincipalId": sp["servicePrincipalId"]
                }
            }

        except Exception as e:
            logging.error(f"Bootstrap failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
