"""
Retourne la liste des langues supportées
"""

import azure.functions as func
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from shared.utils.response_helper import create_response, create_error_response


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retourne la liste des langues supportées
    """
    try:
        from shared.models.schemas import SupportedLanguages
        
        languages = SupportedLanguages.get_all_languages()
        
        return create_response({
            "languages": languages,
            "count": len(languages)
        }, 200)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des langues: {str(e)}")
        return create_error_response(f"Erreur interne: {str(e)}", 500)



