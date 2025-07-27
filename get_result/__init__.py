"""
Récupère l'URL SAS du document traduit
Supporte POST (JSON body) et GET (paramètres URL)
"""

import azure.functions as func
import logging
import os
from datetime import datetime, timezone

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des handlers
from shared.utils.response_helper import create_response, create_error_response, validate_json_request
from shared.services.blob_service import BlobService
from shared.services.graph_service import GraphService
from shared.config import Config

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Récupère l'URL SAS du document traduit
    Supporte POST (JSON body) et GET (paramètres URL)
    """
    logger.info(f"📥 Récupération de résultat - Méthode: {req.method}")
    
    try:
        # Extraction des paramètres selon la méthode HTTP
        if req.method.upper() == 'POST':
            # POST avec JSON body
            if not req.get_body():
                return create_error_response("Corps de requête JSON manquant", 400)
            
            try:
                data = req.get_json()
                if not data:
                    return create_error_response("JSON invalide ou vide", 400)
                    
                blob_name = data.get('blob_name')
                target_language = data.get('target_language')
                user_id = data.get('user_id')
                
                logger.info(f"📋 Paramètres POST - blob: {blob_name}, langue: {target_language}, user: {user_id}")
                
            except Exception as e:
                return create_error_response(f"Erreur de parsing JSON: {str(e)}", 400)
                
        else:
            # GET avec paramètres URL
            blob_name = req.params.get('blob_name')
            target_language = req.params.get('target_language')
            user_id = req.params.get('user_id')
            
            logger.info(f"📋 Paramètres GET - blob: {blob_name}, langue: {target_language}, user: {user_id}")

        # Validation des paramètres obligatoires
        if not blob_name or not target_language:
            missing = []
            if not blob_name:
                missing.append('blob_name')
            if not target_language:
                missing.append('target_language')
            return create_error_response(f"Paramètres manquants: {', '.join(missing)}", 400)
        
        if not blob_name.strip() or not target_language.strip():
            return create_error_response("Les paramètres ne peuvent pas être vides", 400)
        
        # Initialisation des services
        blob_service = BlobService()
        onedrive_upload_enabled = Config.ONEDRIVE_UPLOAD_ENABLED
        
        # Génère le nom du blob de sortie
        try:
            file_base, file_ext = blob_name.rsplit('.', 1)
            output_blob_name = f"{file_base}-{target_language}.{file_ext}"
            logger.info(f"📄 Nom du blob de sortie: {output_blob_name}")
        except ValueError:
            return create_error_response("Nom de fichier invalide (extension manquante)", 400)

        # Génère l'URL SAS pour le téléchargement
        download_url = blob_service.get_translated_file_url(output_blob_name)
        if not download_url:
            return create_error_response(f"Fichier traduit '{output_blob_name}' introuvable", 404)

        result = {
            "blob_name": blob_name,
            "target_language": target_language,
            "output_blob_name": output_blob_name,
            "download_url": download_url,
            "user_id": user_id
        }

        # (Optionnel) Upload vers OneDrive si configuré et user_id fourni
        if onedrive_upload_enabled and user_id:
            try:
                graph_service = GraphService()
                file_content = blob_service.download_translated_file(output_blob_name)
                if file_content:
                    onedrive_result = graph_service.upload_to_onedrive(file_content, output_blob_name, user_id)
                    if onedrive_result.get("success"):
                        result["onedrive_url"] = onedrive_result.get("onedrive_url")
                        logger.info("✅ Fichier uploadé vers OneDrive")
                    else:
                        result["onedrive_error"] = onedrive_result.get("error")
                        logger.warning(f"⚠️ Erreur OneDrive: {onedrive_result.get('error')}")
                else:
                    result["onedrive_error"] = "Impossible de télécharger le fichier pour OneDrive"
            except Exception as onedrive_error:
                result["onedrive_error"] = f"Erreur OneDrive: {str(onedrive_error)}"
                logger.error(f"❌ Erreur OneDrive: {str(onedrive_error)}")

        logger.info(f"✅ Résultat préparé pour {blob_name} -> {target_language}")
        return create_response(result, 200)

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du résultat: {str(e)}")
        return create_error_response(f"Erreur interne: {str(e)}", 500)
