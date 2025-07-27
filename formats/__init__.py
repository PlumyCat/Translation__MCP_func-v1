"""
Retourne la liste des langues supportées
"""

import azure.functions as func
import json
import logging
import os
from typing import Dict, Any
from datetime import datetime, timezone

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application Azure Functions
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

from shared.utils.response_helper import create_response, create_error_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retourne la liste des formats de fichiers supportés
    """
    try:
        from shared.models.schemas import FileFormats
        
        formats = FileFormats.get_all_formats()
        
        return create_response({
            "formats": formats,
            "count": len(formats)
        }, 200)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des formats: {str(e)}")
        return create_error_response(f"Erreur interne: {str(e)}", 500)
