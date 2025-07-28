"""
Handler pour la gestion des statuts de traduction
Remplace le polling de la fonction durable
"""

import logging
import time
from typing import Dict, Any, Optional
from shared.services.translation_service import TranslationService
from shared.services.blob_service import BlobService
from shared.services.graph_service import GraphService
from shared.models.schemas import TranslationStatus, TranslationResult

logger = logging.getLogger(__name__)


class StatusHandler:
    """Handler pour vérifier et gérer les statuts de traduction"""

    def __init__(self):
        self.translation_service = TranslationService()
        self.blob_service = BlobService()
        self.graph_service = GraphService()
        self.translation_id = None
        
        logger.info("✅ StatusHandler initialisé")
    
    def check_status(self, translation_id: str) -> dict:
        """Interroge directement Azure Translator."""
        try:
            status = self.translation_service.check_translation_status(translation_id)
            response_data = {
                "translation_id": translation_id,
                "status": status.get("status")
            }
            if status.get("status") == "Failed":
                response_data["error"] = status.get("error", "Erreur inconnue")

            return {
                "success": True,
                "data": response_data
            }
        except Exception as e:
            logger.error(f"❌ Erreur vérification statut: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors de la vérification: {str(e)}"
            }

    def get_result(self, translation_id: str) -> Dict[str, Any]:
        """
        Récupère le résultat complet d'une traduction terminée
        Inclut le téléchargement et l'upload OneDrive
        """
        logger.info(f"📥 Récupération du résultat: {translation_id}")

        try:
            # Vérification du statut d'abord
            status_result = self.check_status(translation_id)
            if not status_result["success"]:
                return status_result

            status_data = status_result["data"]
            current_status = status_data.get("status")

            # Vérifier que la traduction est terminée
            if current_status not in [TranslationStatus.SUCCEEDED.value, TranslationStatus.FAILED.value]:
                return {
                    "success": False,
                    "message": f"Traduction non terminée (statut: {current_status})"
                }

            # Pour les traductions échouées
            if current_status == TranslationStatus.FAILED.value:
                return {
                    "success": True,
                    "data": {
                        "translation_id": translation_id,
                        "status": current_status,
                        "error": status_data.get("error", "Traduction échouée"),
                        "file_name": status_data.get("file_name"),
                        "target_language": status_data.get("target_language")
                    }
                }

            # Pour les traductions réussies - information limitée car pas de state manager
            # Dans Azure Functions v1, on retourne directement le statut d'Azure Translator
            return {
                "success": True,
                "data": {
                    "translation_id": translation_id,
                    "status": current_status,
                    "message": "Traduction terminée avec succès",
                    "note": "Utilisez l'endpoint get_result pour récupérer le fichier traduit"
                }
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération du résultat: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur de récupération: {str(e)}"
            }

    def _prepare_download_info(self, translation_info) -> Dict[str, Any]:
        """Prépare les informations de téléchargement"""
        try:
            output_blob_name = translation_info.blob_urls.output_blob_name
            
            # Génération de l'URL de téléchargement
            download_url = self.blob_service.get_translated_file_url(output_blob_name)
            
            download_info = {}
            if download_url:
                download_info["download_url"] = download_url
                download_info["download_expires_at"] = time.time() + (24 * 3600)  # 24h
                logger.info("✅ URL de téléchargement générée")
            else:
                download_info["download_error"] = "Fichier traduit introuvable"
                logger.warning("⚠️ Fichier traduit introuvable")

            return download_info

        except Exception as e:
            logger.error(f"❌ Erreur préparation téléchargement: {str(e)}")
            return {"download_error": f"Erreur: {str(e)}"}

    def _prepare_final_result(self, translation_info, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare le résultat final avec toutes les options de récupération"""
        output_blob_name = translation_info.blob_urls.output_blob_name
        
        result = {
            "translation_id": status_data["translation_id"],
            "status": status_data["status"],
            "file_name": translation_info.file_name,
            "target_language": translation_info.target_language,
            "user_id": translation_info.user_id
        }

        # Option 1: URL de téléchargement direct
        download_url = self.blob_service.get_translated_file_url(output_blob_name)
        if download_url:
            result["download_url"] = download_url
            result["download_expires_at"] = time.time() + (24 * 3600)  # 24h

        # Option 2: Upload vers OneDrive (si configuré)
        if self.graph_service.is_configured():
            try:
                # Téléchargement du fichier depuis le blob
                file_content = self.blob_service.download_translated_file(output_blob_name)
                if file_content:
                    # Upload vers OneDrive
                    onedrive_result = self.graph_service.upload_to_onedrive(
                        file_content=file_content,
                        file_name=f"{translation_info.file_name}",
                        user_id=translation_info.user_id
                    )
                    
                    if onedrive_result["success"]:
                        result["onedrive_url"] = onedrive_result["onedrive_url"]
                        result["onedrive_file_id"] = onedrive_result.get("file_id")
                        logger.info("✅ Fichier uploadé vers OneDrive")
                    else:
                        result["onedrive_error"] = onedrive_result["error"]
                        logger.warning(f"⚠️ Erreur upload OneDrive: {onedrive_result['error']}")
                else:
                    result["onedrive_error"] = "Fichier traduit inaccessible"
            except Exception as e:
                result["onedrive_error"] = f"Erreur upload: {str(e)}"
                logger.error(f"❌ Erreur upload OneDrive: {str(e)}")

        return result

    def _cleanup_after_completion(self, translation_info) -> None:
        """Nettoie les ressources après completion"""
        try:
            # Nettoyage des blobs après un délai (optionnel)
            # En production, on pourrait vouloir garder les fichiers plus longtemps
            cleanup_delay_hours = 1
            
            # Programmer le nettoyage (en production, utiliser une queue ou un timer)
            # Pour l'instant, on ne fait qu'enregistrer l'intention
            logger.info(f"🗑️ Nettoyage programmé dans {cleanup_delay_hours}h")
            
        except Exception as e:
            logger.error(f"❌ Erreur programmation nettoyage: {str(e)}")

