"""
Azure Function: Import Solution
Importe une solution Power Platform dans un environnement Dataverse
"""

import logging
import json
import os
import azure.functions as func

from shared.powerplatform_service import PowerPlatformCredentials, PowerPlatformService

logger = logging.getLogger(__name__)

# Chemin vers la solution embarquee
SOLUTION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "..", "solution", "TranslationDeploymentBot.zip"
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Importe la solution dans un environnement Dataverse"""
    logger.info("Import Solution request received")

    try:
        body = req.get_json()

        # Parametres requis
        environment_url = body.get("environmentUrl")
        tenant_id = body.get("tenantId")
        client_id = body.get("clientId")
        client_secret = body.get("clientSecret")

        # Parametres optionnels
        solution_path = body.get("solutionPath", SOLUTION_PATH)
        overwrite = body.get("overwrite", True)

        if not all([environment_url, tenant_id, client_id, client_secret]):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing required parameters: environmentUrl, tenantId, clientId, clientSecret"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Verifier que la solution existe
        if not os.path.exists(solution_path):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Solution file not found: {solution_path}. Please upload the solution ZIP file."
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
        result = service.import_solution(
            environment_url=environment_url,
            solution_path=solution_path,
            overwrite=overwrite
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
        logger.error(f"Error importing solution: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
