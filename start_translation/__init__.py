"""
Démarre une nouvelle traduction de document
"""

import azure.functions as func
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des helpers et handlers
from shared.utils.response_helper import (
    create_response,
    create_error_response,
    validate_json_request,
)
from shared.services.translation_handler import TranslationHandler

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Démarre une nouvelle traduction de document
    """
    logger.info("🚀 Démarrage d'une nouvelle traduction")

    try:
        # Validation et extraction du corps JSON
        success, data_or_resp = validate_json_request(
            req, ["file_content", "file_name", "target_language", "user_id"]
        )
        if not success:
            return data_or_resp

        file_content = data_or_resp.get("file_content")
        file_name = data_or_resp.get("file_name")
        target_language = data_or_resp.get("target_language")
        user_id = data_or_resp.get("user_id")

        # Démarrage du processus de traduction via le handler
        handler = TranslationHandler()
        result = handler.start_translation(
            file_content=file_content,
            file_name=file_name,
            target_language=target_language,
            user_id=user_id,
        )

        if not result.get("success"):
            return create_error_response(
                result.get("message", "Erreur lors du démarrage de la traduction"),
                400,
            )

        data = result.get("data", {})
        response_data = {
            "translation_id": data.get("translation_id"),
            "azure_translation_id": data.get("azure_translation_id"),
            "status": data.get("status"),
        }
        return create_response(response_data, 202)

    except Exception as e:
        logger.error(f"❌ Erreur traduction: {str(e)}")
        return create_error_response(f"Erreur lors de la traduction: {str(e)}", 500)

