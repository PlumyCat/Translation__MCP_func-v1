"""
Handler pour orchestrer le processus de traduction
Remplace la fonction durable orchestrator
"""

import logging
import uuid
import time
from typing import Dict, Any
from shared.services.blob_service import BlobService
from shared.services.translation_service import TranslationService
from shared.services.state_manager import StateManager
from shared.models.schemas import (
    TranslationRequest, 
    TranslationInfo, 
    TranslationStatus,
    validate_file_format,
    validate_language_code
)
from shared.config import Config

logger = logging.getLogger(__name__)


class TranslationHandler:
    """Handler pour orchestrer les traductions de documents"""

    def __init__(self):
        self.blob_service = BlobService()
        self.translation_service = TranslationService()
        self.state_manager = StateManager()
        self.max_age_hours = Config.CLEANUP_INTERVAL_HOURS

        logger.info("✅ TranslationHandler initialisé")

    def start_translation(self, file_content: str, file_name: str, 
                         target_language: str, user_id: str) -> Dict[str, Any]:
        """
        Démarre une nouvelle traduction
        Remplace l'orchestrator de la fonction durable
        """
        logger.info(f"🚀 Nouveau processus de traduction pour {user_id}")
        logger.info(f"📄 Fichier: {file_name} → {target_language}")

        try:
            # Validation des paramètres
            validation_errors = self._validate_request(file_content, file_name, target_language, user_id)
            if validation_errors:
                return {
                    "success": False,
                    "message": f"Erreurs de validation: {', '.join(validation_errors)}"
                }

            # Génération d'un ID unique pour cette traduction
            translation_id = str(uuid.uuid4())
            logger.info(f"🆔 ID de traduction généré: {translation_id}")

            # Étape 1: Préparation des blobs Azure Storage
            logger.info("📁 Étape 1: Préparation des blobs...")
            try:
                blob_urls = self.blob_service.prepare_blobs(
                    file_content_base64=file_content,
                    file_name=file_name,
                    target_language=target_language
                )
                logger.info("✅ Blobs préparés avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur préparation blobs: {str(e)}")
                return {
                    "success": False,
                    "message": f"Erreur de préparation des fichiers: {str(e)}"
                }

            # Étape 2: Démarrage de la traduction Azure
            logger.info("🔄 Étape 2: Démarrage de la traduction...")
            try:
                azure_translation_id = self.translation_service.start_translation(
                    source_url=blob_urls["source_url"],
                    target_url=blob_urls["target_url"],
                    target_language=target_language
                )
                logger.info(f"✅ Traduction démarrée avec l'ID Azure: {azure_translation_id}")
            except Exception as e:
                logger.error(f"❌ Erreur démarrage traduction: {str(e)}")
                # Nettoyage des blobs en cas d'erreur
                self.blob_service.cleanup_translation_files(
                    blob_urls["input_blob_name"], 
                    blob_urls["output_blob_name"]
                )
                return {
                    "success": False,
                    "message": f"Erreur de démarrage de traduction: {str(e)}"
                }

            # Étape 3: Sauvegarde de l'état
            logger.info("💾 Étape 3: Sauvegarde de l'état...")
            translation_info = TranslationInfo(
                file_name=file_name,
                target_language=target_language,
                user_id=user_id,
                blob_urls=blob_urls,
                status=TranslationStatus.IN_PROGRESS.value,
                started_at=time.time(),
                translation_id=azure_translation_id
            )

            success = self.state_manager.save_translation_state(translation_id, translation_info)
            if not success:
                logger.warning("⚠️ Impossible de sauvegarder l'état (continuons quand même)")

            # Retour du résultat
            result = {
                "translation_id": translation_id,
                "azure_translation_id": azure_translation_id,
                "status": TranslationStatus.IN_PROGRESS.value,
                "message": "Traduction démarrée avec succès",
                "file_name": file_name,
                "target_language": target_language,
                "started_at": time.time()
            }

            logger.info(f"✅ Traduction {translation_id} démarrée avec succès")
            return {
                "success": True,
                "message": "Traduction démarrée",
                "data": result
            }

        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors du démarrage: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur interne: {str(e)}"
            }

    def cancel_translation(self, translation_id: str) -> Dict[str, Any]:
        """
        Annule une traduction en cours
        """
        logger.info(f"🛑 Annulation de la traduction: {translation_id}")

        try:
            # Récupération de l'état de la traduction
            translation_info = self.state_manager.get_translation_state(translation_id)
            if not translation_info:
                return {
                    "success": False,
                    "message": "Traduction introuvable"
                }

            # Annulation côté Azure Translator
            azure_success = self.translation_service.cancel_translation(
                translation_info.translation_id
            )

            # Nettoyage des blobs
            cleanup_success = self.blob_service.cleanup_translation_files(
                translation_info.blob_urls.input_blob_name,
                translation_info.blob_urls.output_blob_name
            )

            # Mise à jour de l'état
            translation_info.status = TranslationStatus.FAILED.value
            self.state_manager.save_translation_state(translation_id, translation_info)

            # Suppression de l'état après un délai
            self.state_manager.delete_translation_state(translation_id, delay_minutes=5)

            success_msg = "Traduction annulée"
            if not azure_success:
                success_msg += " (erreur annulation Azure)"
            if not cleanup_success:
                success_msg += " (erreur nettoyage fichiers)"

            logger.info(f"✅ {success_msg}: {translation_id}")
            return {
                "success": True,
                "message": success_msg
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'annulation: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur d'annulation: {str(e)}"
            }

    def _validate_request(self, file_content: str, file_name: str, 
                         target_language: str, user_id: str) -> list:
        """Valide les paramètres de la requête"""
        errors = []

        # Validation du contenu du fichier
        if not file_content or not file_content.strip():
            errors.append("Contenu du fichier manquant")

        # Validation du nom de fichier
        if not file_name or not file_name.strip():
            errors.append("Nom du fichier manquant")
        elif not validate_file_format(file_name):
            errors.append(f"Format de fichier non supporté: {file_name}")

        # Validation de la langue
        if not target_language or not target_language.strip():
            errors.append("Langue cible manquante")
        elif not validate_language_code(target_language):
            errors.append(f"Code de langue non supporté: {target_language}")

        # Validation de l'utilisateur
        if not user_id or not user_id.strip():
            errors.append("ID utilisateur manquant")

        return errors

    def get_active_translations_count(self, user_id) -> int:
        """Compte le nombre de traductions actives"""
        try:
            return self.state_manager.count_active_translations(user_id)
        except Exception as e:
            logger.error(f"❌ Erreur comptage traductions: {str(e)}")
            return 0

    def cleanup_old_translations(self, max_age_hours: int = 2) -> int:
        """Nettoie les anciennes traductions"""
        try:
            return self.state_manager.cleanup_old_translations(max_age_hours)
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage traductions: {str(e)}")
            return 0