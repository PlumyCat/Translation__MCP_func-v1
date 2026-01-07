"""
Azure Function: List Deployments
Retourne la liste des deploiements effectues
"""

import logging
import json
import azure.functions as func

from shared.deployment_store import get_store

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Liste les deploiements"""
    logger.info("List deployments request received")

    try:
        # Parametres de filtre optionnels
        region = req.params.get("region")
        status = req.params.get("status")

        # Recuperer les deploiements
        store = get_store()
        records = store.list(region=region, status=status)

        # Formater la reponse
        deployments = []
        for record in records:
            deployments.append({
                "clientName": record.client_name,
                "region": record.region,
                "status": record.status,
                "deployedAt": record.deployed_at,
                "functionAppUrl": record.function_app_url
            })

        return func.HttpResponse(
            json.dumps({
                "deployments": deployments,
                "total": len(deployments)
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
