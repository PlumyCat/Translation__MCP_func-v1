"""
Bootstrap Complete - Complete le Device Code Flow et cree le Service Principal
Etape 2: Poll pour l'auth, puis cree App Registration + SP + assigne role Contributor
"""
import logging
import json
import azure.functions as func
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.bootstrap_service import BootstrapService

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Bootstrap complete - Poll and create SP')

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
    device_code = req_body.get('deviceCode')
    app_name = req_body.get('appName', 'SP-Translation-Deployment')

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

    if not device_code:
        return func.HttpResponse(
            json.dumps({"success": False, "error": "deviceCode est requis (obtenu via bootstrap-client)"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        # Etape 1: Poll pour obtenir le token (attend que l'utilisateur complete l'auth)
        logging.info("Polling for device code authentication...")
        tokens = BootstrapService.poll_device_code(
            tenant_id=tenant_id,
            device_code=device_code,
            interval=5,
            timeout=300  # 5 minutes max
        )

        logging.info("Authentication successful, creating Service Principal...")

        # Etape 2: Creer le Service Principal avec le token obtenu
        service = BootstrapService(
            tenant_id=tenant_id,
            subscription_id=subscription_id
        )
        service.set_tokens_from_device_code(tokens["access_token"])

        # Creer l'App Registration
        app = service.create_app_registration(app_name)
        logging.info(f"App Registration created: {app['appId']}")

        # Creer le Service Principal
        sp = service.create_service_principal(app["appId"])
        logging.info(f"Service Principal created: {sp['servicePrincipalId']}")

        # Creer le Client Secret
        secret = service.create_client_secret(app["objectId"])
        logging.info("Client secret created")

        # Assigner le role Contributor
        service.assign_contributor_role(sp["servicePrincipalId"])
        logging.info("Contributor role assigned")

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Service Principal cree avec succes",
                "credentials": {
                    "tenantId": tenant_id,
                    "subscriptionId": subscription_id,
                    "clientId": app["appId"],
                    "clientSecret": secret["secretValue"],
                    "secretExpiresAt": secret["expiresAt"]
                },
                "details": {
                    "appName": app["displayName"],
                    "appObjectId": app["objectId"],
                    "servicePrincipalId": sp["servicePrincipalId"]
                }
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Bootstrap complete error: {str(e)}")

        # Message specifique selon l'erreur
        error_msg = str(e)
        if "authorization_pending" in error_msg.lower():
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "authPending": True,
                    "error": "L'utilisateur n'a pas encore complete l'authentification. Reessayez dans quelques secondes."
                }),
                status_code=202,  # Accepted - still processing
                mimetype="application/json"
            )

        return func.HttpResponse(
            json.dumps({"success": False, "error": error_msg}),
            status_code=500,
            mimetype="application/json"
        )
