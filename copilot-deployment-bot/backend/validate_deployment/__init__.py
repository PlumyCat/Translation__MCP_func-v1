"""
Azure Function: Validate Deployment
Execute des tests de validation sur un deploiement existant
"""

import logging
import json
import azure.functions as func

from shared.azure_deployer import DeploymentValidator

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Valide un deploiement existant"""
    logger.info("Validate deployment request received")

    try:
        # Parser le body
        body = req.get_json()

        function_app_url = body.get("functionAppUrl")
        function_key = body.get("functionKey", "")

        # Validation des parametres requis
        if not function_app_url:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameter: functionAppUrl"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Valider le format de l'URL
        if not function_app_url.startswith("https://"):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "functionAppUrl must start with https://"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Executer la validation
        validator = DeploymentValidator(function_app_url, function_key)
        result = validator.validate()

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
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
        logger.error(f"Error validating deployment: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
