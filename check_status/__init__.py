"""
Vérifie le statut d'une traduction en cours
Route: GET /api/check_status/{translation_id}
"""

import azure.functions as func
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des handlers
from shared.services.status_handler import StatusHandler
from shared.utils.response_helper import create_response, create_error_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Vérifie le statut d'une traduction en cours
    Route: GET /api/check_status/{translation_id}
    """
    try:
        # Récupération de l'ID de traduction depuis la route
        translation_id = req.route_params.get('translation_id')
        
        if not translation_id:
            return create_error_response("ID de traduction manquant dans l'URL", 400)
        
        if not translation_id.strip():
            return create_error_response("ID de traduction vide", 400)
            
        logger.info(f"🔍 Vérification du statut pour: {translation_id}")
        
        # Initialisation du handler
        status_handler = StatusHandler()
        
        # Vérification du statut
        result = status_handler.check_status(translation_id)
        
        if result['success']:
            return create_response(result['data'], 200)
        else:
            return create_error_response(result['message'], 404)
            
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la vérification du statut: {str(e)}")
        return create_error_response(f"Erreur interne: {str(e)}", 500)

