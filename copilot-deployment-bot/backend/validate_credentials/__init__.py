"""
Azure Function: Validate Credentials
Valide les credentials Azure du client
"""

import logging
import json
import azure.functions as func

from shared.azure_deployer import AzureCredentials, AzureDeployer, DeploymentConfig

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Valide les credentials Azure"""
    logger.info("Validate credentials request received")

    try:
        # Parser le body
        body = req.get_json()

        subscription_id = body.get("subscriptionId")
        tenant_id = body.get("tenantId")
        client_id = body.get("clientId")
        client_secret = body.get("clientSecret")

        # Validation des parametres requis
        if not all([subscription_id, tenant_id, client_id, client_secret]):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameters: subscriptionId, tenantId, clientId, clientSecret"
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

        # Creer une config temporaire pour le deployer
        config = DeploymentConfig(client_name="validation", region="francecentral")

        # Valider les credentials
        deployer = AzureDeployer(credentials, config)
        result = deployer.validate_credentials()

        return func.HttpResponse(
            json.dumps(result),
            status_code=200 if result["success"] else 401,
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
        logger.error(f"Error validating credentials: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
