"""
Point de santé pour vérifier que les fonctions sont opérationnelles
"""

import azure.functions as func
import logging
import os
from datetime import datetime, timezone

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des handlers
from shared.utils.response_helper import create_response, create_error_response
from shared.config import Config

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Point de santé pour vérifier que les fonctions sont opérationnelles
    """
    try:
        # Vérification des variables d'environnement critiques
        required_vars = [
            'TRANSLATOR_KEY',
            'TRANSLATOR_ENDPOINT',
            'AZURE_ACCOUNT_NAME',
            'AZURE_ACCOUNT_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return create_error_response(
                f"Variables d'environnement manquantes: {', '.join(missing_vars)}", 
                503
            )
        
        # Vérification OneDrive
        onedrive_upload_enabled = Config.ONEDRIVE_UPLOAD_ENABLED
        if onedrive_upload_enabled:
            od_available = "available"
        else:
            od_available = "not configured"
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "translator": "available",
                "blob_storage": "available",
                "onedrive": od_available
            }
        }
        
        return create_response(health_data, 200)
        
    except Exception as e:
        logger.error(f"❌ Erreur du health check: {str(e)}")
        return create_error_response(f"Service unhealthy: {str(e)}", 503)
