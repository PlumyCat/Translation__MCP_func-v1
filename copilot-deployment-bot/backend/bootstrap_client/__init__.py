"""
Bootstrap Client - Cree automatiquement le Service Principal chez le client
"""
import logging
import json
import azure.functions as func
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.bootstrap_service import BootstrapService

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Bootstrap client request received')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"success": False, "error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    # Parametres requis
    tenant_id = req_body.get('tenantId')
    subscription_id = req_body.get('subscriptionId')

    # Option 1: Admin username/password (pour auth interactive ou ROPC)
    admin_username = req_body.get('adminUsername')
    admin_password = req_body.get('adminPassword')

    # Option 2: Service Principal admin existant
    admin_client_id = req_body.get('adminClientId')
    admin_client_secret = req_body.get('adminClientSecret')

    # Nom de l'application a creer
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

    # Verifier qu'on a soit admin user/pass, soit admin SP
    has_user_creds = admin_username and admin_password
    has_sp_creds = admin_client_id and admin_client_secret

    if not has_user_creds and not has_sp_creds:
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Fournir soit adminUsername/adminPassword, soit adminClientId/adminClientSecret"
            }),
            status_code=400,
            mimetype="application/json"
        )

    try:
        service = BootstrapService(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            admin_username=admin_username,
            admin_password=admin_password,
            admin_client_id=admin_client_id,
            admin_client_secret=admin_client_secret
        )

        result = service.bootstrap_client(app_name=app_name)

        return func.HttpResponse(
            json.dumps(result),
            status_code=200 if result.get('success') else 500,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Bootstrap error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
