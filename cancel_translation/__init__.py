"""
Annule une traduction en cours
Route: DELETE /api/cancel_translation/{translation_id}
"""

import azure.functions as func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from shared.utils.response_helper import create_response, create_error_response
from shared.services.translation_handler import TranslationHandler

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Annule une traduction en cours"""
    try:
        translation_id = req.route_params.get('translation_id') or req.params.get('translation_id')

        if not translation_id:
            return create_error_response("ID de traduction manquant", 400)
        if not translation_id.strip():
            return create_error_response("ID de traduction vide", 400)

        logger.info(f"🛑 Annulation demandée pour: {translation_id}")

        handler = TranslationHandler()
        result = handler.cancel_translation(translation_id)

        if result.get("success"):
            data = {"translation_id": translation_id, "message": result.get("message")}
            return create_response(data, 200)
        else:
            message = result.get("message", "Erreur d'annulation")
            status_code = 404 if "introuvable" in message.lower() else 500
            return create_error_response(message, status_code)

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'annulation: {str(e)}")
        return create_error_response(f"Erreur interne: {str(e)}", 500)
