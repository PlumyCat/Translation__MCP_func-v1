"""
Azure Function: Get Deployment Status
Retourne le statut d'un deploiement specifique
"""

import logging
import json
import azure.functions as func

from shared.deployment_store import get_store
from shared.azure_deployer import DeploymentValidator

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Obtient le statut d'un deploiement"""
    logger.info("Get deployment status request received")

    try:
        # Recuperer le nom du client depuis la route
        client_name = req.route_params.get("clientName")

        if not client_name:
            return func.HttpResponse(
                json.dumps({"found": False, "error": "Client name is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Recuperer le deploiement
        store = get_store()
        record = store.get(client_name)

        if not record:
            return func.HttpResponse(
                json.dumps({"found": False}),
                status_code=404,
                mimetype="application/json"
            )

        # Verifier la sante du service si le deploiement est actif
        health_status = "Unknown"
        if record.status == "Active" and record.function_app_url:
            try:
                validator = DeploymentValidator(record.function_app_url, record.function_key)
                validation = validator.validate()
                if validation["health_score"] == 100:
                    health_status = "Healthy"
                elif validation["health_score"] >= 60:
                    health_status = "Degraded"
                else:
                    health_status = "Unhealthy"
            except Exception:
                health_status = "Unknown"

        return func.HttpResponse(
            json.dumps({
                "found": True,
                "clientName": record.client_name,
                "status": record.status,
                "deployedAt": record.deployed_at,
                "region": record.region,
                "resourceGroup": record.resource_group,
                "resourceGroupStatus": "Active" if record.status == "Active" else "Unknown",
                "storageAccount": record.storage_account,
                "storageStatus": "Active" if record.status == "Active" else "Unknown",
                "translator": record.translator_name,
                "translatorStatus": "Active" if record.status == "Active" else "Unknown",
                "functionApp": record.function_app_name,
                "functionAppStatus": "Active" if record.status == "Active" else "Unknown",
                "functionAppUrl": record.function_app_url,
                "healthStatus": health_status
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error getting deployment status: {e}")
        return func.HttpResponse(
            json.dumps({"found": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
