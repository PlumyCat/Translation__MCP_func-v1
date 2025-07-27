"""
Démarre une nouvelle traduction de document
"""

import azure.functions as func
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des handlers
from shared.utils.response_helper import create_response, create_error_response
from shared.services.blob_service import BlobService
from shared.services.translation_service import TranslationService

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Démarre une nouvelle traduction de document
    """
    logger.info("🚀 Démarrage d'une nouvelle traduction")

    try:
        if not req.get_body():
            return create_error_response("Corps de requête manquant", 400)

        try:
            data = req.get_json()
        except ValueError as e:
            return create_error_response(f"JSON invalide: {str(e)}", 400)

        required_fields = ["blob_name", "target_language", "user_id"]
        for field in required_fields:
            if field not in data:
                return create_error_response(f"Paramètre manquant: {field}", 400)

        blob_name = data["blob_name"]
        target_language = data["target_language"]
        user_id = data["user_id"]

        # 1. Vérifier l’existence du blob
        blob_service = BlobService()
        if not blob_service.check_blob_exists(blob_name):
            return create_error_response(f"Fichier '{blob_name}' non trouvé", 404)

        # 2. Construire les URLs SAS
        blob_urls = blob_service.prepare_translation_urls(blob_name, target_language)
        source_url = blob_urls["source_url"]
        target_url = blob_urls["target_url"]

        # 3. Démarrer la traduction
        translation_service = TranslationService()
        translation_id = translation_service.start_translation(
            source_url=source_url,
            target_url=target_url,
            target_language=target_language
        )

        result = {
            "success": True,
            "translation_id": translation_id,
            "message": f"Traduction démarrée avec succès pour {blob_name}",
            "status": "En cours",
            "target_language": target_language,
            "estimated_time": "2-5 minutes"
        }
        return create_response(result, 202)

    except Exception as e:
        logger.error(f"❌ Erreur traduction: {str(e)}")
        return create_error_response(f"Erreur lors de la traduction: {str(e)}", 500)

