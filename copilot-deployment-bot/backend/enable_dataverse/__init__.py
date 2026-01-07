"""
Azure Function: Enable Dataverse
Active Dataverse en creant un nouvel environnement Power Platform
"""

import logging
import json
import azure.functions as func

from shared.powerplatform_service import PowerPlatformCredentials, PowerPlatformService

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Cree un environnement avec Dataverse active"""
    logger.info("Enable Dataverse request received")

    try:
        body = req.get_json()

        # Parametres requis
        environment_name = body.get("environmentName")
        tenant_id = body.get("tenantId")
        client_id = body.get("clientId")
        client_secret = body.get("clientSecret")

        # Parametres optionnels
        region = body.get("region", "france")
        environment_type = body.get("environmentType", "Production")
        currency = body.get("currency", "EUR")
        language = body.get("language", 1036)

        if not all([environment_name, tenant_id, client_id, client_secret]):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameters: environmentName, tenantId, clientId, clientSecret"
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
        result = service.enable_dataverse(
            environment_name=environment_name,
            region=region,
            environment_type=environment_type,
            currency=currency,
            language=language
        )

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
        logger.error(f"Error enabling Dataverse: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
