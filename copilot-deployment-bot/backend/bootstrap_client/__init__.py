"""
Bootstrap Client - Demarre le Device Code Flow pour authentification admin
Etape 1: Retourne le code et l'URL pour que le tech s'authentifie
"""
import logging
import json
import azure.functions as func
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.bootstrap_service import BootstrapService

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Bootstrap client - Start device code flow')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"success": False, "error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    tenant_id = req_body.get('tenantId')
    subscription_id = req_body.get('subscriptionId')

    if not tenant_id:
        return func.HttpResponse(
            json.dumps({"success": False, "error": "tenantId est requis"}),
            status_code=400,
            mimetype="application/json"
        )

    if not subscription_id:
        return func.HttpResponse(
            json.dumps({"success": False, "error": "subscriptionId est requis"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        # Demarrer le device code flow
        result = BootstrapService.start_device_code_flow(tenant_id)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "authPending": True,
                "tenantId": tenant_id,
                "subscriptionId": subscription_id,
                "deviceCode": result["device_code"],
                "userCode": result["user_code"],
                "verificationUri": result["verification_uri"],
                "message": result["message"],
                "expiresIn": result["expires_in"],
                "interval": result["interval"],
                "instructions": f"Demandez au tech d'aller sur {result['verification_uri']} et d'entrer le code: {result['user_code']}"
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Bootstrap start error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
