"""
Azure Function: Check Dataverse
Verifie si Dataverse est active dans un environnement Power Platform
"""

import logging
import json
import azure.functions as func

from shared.powerplatform_service import PowerPlatformCredentials, PowerPlatformService

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Verifie si Dataverse est active"""
    logger.info("Check Dataverse request received")

    try:
        body = req.get_json()

        # Parametres requis
        environment_id = body.get("environmentId") or body.get("environmentName")
        tenant_id = body.get("tenantId")
        client_id = body.get("clientId")
        client_secret = body.get("clientSecret")

        if not all([environment_id, tenant_id, client_id, client_secret]):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameters: environmentId/environmentName, tenantId, clientId, clientSecret"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Creer le service
        credentials = PowerPlatformCredentials(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        service = PowerPlatformService(credentials)
        result = service.check_dataverse(environment_id)

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
        logger.error(f"Error checking Dataverse: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
