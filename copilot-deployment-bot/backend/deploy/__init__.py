"""
Azure Function: Full Deployment
Execute le deploiement complet du service de traduction
"""

import logging
import json
import azure.functions as func

from shared.azure_deployer import AzureCredentials, AzureDeployer, DeploymentConfig
from shared.deployment_store import get_store, DeploymentRecord

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Execute le deploiement complet"""
    logger.info("Full deployment request received")

    try:
        # Parser le body
        body = req.get_json()

        # Parametres requis
        client_name = body.get("clientName")
        region = body.get("region", "francecentral")
        subscription_id = body.get("subscriptionId")
        tenant_id = body.get("tenantId")
        client_id = body.get("clientId")
        client_secret = body.get("clientSecret")

        # Parametres optionnels OneDrive
        enable_onedrive = body.get("enableOneDrive", False)
        onedrive_config = body.get("oneDriveConfig", {})

        # Validation des parametres requis
        if not all([client_name, subscription_id, tenant_id, client_id, client_secret]):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameters"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Valider le format du nom de client
        import re
        if not re.match(r"^[a-z0-9-]+$", client_name):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Client name must contain only lowercase letters, numbers, and hyphens"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Creer les credentials
        credentials = AzureCredentials(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        # Creer la configuration
        config = DeploymentConfig(
            client_name=client_name,
            region=region,
            enable_onedrive=enable_onedrive,
            onedrive_client_id=onedrive_config.get("clientId"),
            onedrive_client_secret=onedrive_config.get("clientSecret"),
            onedrive_tenant_id=onedrive_config.get("tenantId"),
            onedrive_folder=onedrive_config.get("folderName", "Translated_Documents")
        )

        # Executer le deploiement
        deployer = AzureDeployer(credentials, config)
        result = deployer.full_deployment()

        # Enregistrer le deploiement
        if result.success:
            store = get_store()
            record = DeploymentRecord(
                client_name=client_name,
                deployment_id=result.deployment_id,
                region=region,
                status="Active",
                deployed_at=result.deployed_at,
                resource_group=result.resource_group,
                storage_account=result.storage_account_name,
                translator_name=config.translator_name,
                function_app_name=config.function_app_name,
                function_app_url=result.function_app_url,
                function_key=result.function_key
            )
            store.add(record)

        return func.HttpResponse(
            json.dumps(result.to_dict()),
            status_code=200 if result.success else 500,
            mimetype="application/json"
        )

    except ValueError as e:
        logger.error(f"Invalid JSON body: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error during deployment: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
