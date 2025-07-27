"""
Service de traduction Azure Translator pour Azure Functions
Adapté du code conteneur existant
"""

import logging
import requests
from typing import Dict, Any, Optional
from shared.config import Config

logger = logging.getLogger(__name__)


class TranslationService:
    """Service pour la traduction de documents via Azure Translator"""

    def __init__(self):
        # Configuration Azure Translator
        self.trans_key = Config.TRANSLATOR_KEY
        self.trans_endpoint = Config.TRANSLATOR_ENDPOINT

        if not self.trans_key:
            raise ValueError("TRANSLATOR_KEY non définie")
        if not self.trans_endpoint:
            raise ValueError("TRANSLATOR_ENDPOINT non définie")

        # Assurer que l'endpoint se termine par "/"
        if not self.trans_endpoint.endswith("/"):
            self.trans_endpoint += "/"

        # URL de base pour l'API Batch Translation
        self.batch_api_url = Config.get_translator_batch_url()

        # Headers communs
        self.headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.trans_key
        }

        logger.info("✅ TranslationService initialisé")

    def start_translation(self, source_url: str, target_url: str, target_language: str) -> str:
        """
        Démarre une traduction batch
        Version synchrone pour Azure Functions
        """
        logger.info(f"🚀 Démarrage traduction batch vers {target_language}")
        logger.info(f"📂 Source: {source_url}")
        logger.info(f"📁 Target: {target_url}")

        try:
            # Corps de la requête pour l'API Batch Translation
            body = {
                "inputs": [
                    {
                        "storageType": "File",
                        "source": {
                            "sourceUrl": source_url
                        },
                        "targets": [
                            {
                                "targetUrl": target_url,
                                "language": target_language
                            }
                        ]
                    }
                ]
            }

            # Envoi de la requête
            logger.info("📤 Envoi de la requête de traduction...")
            response = requests.post(
                self.batch_api_url,
                headers=self.headers,
                json=body,
                timeout=30
            )

            # Vérification de la réponse
            if response.status_code != 202:  # 202 = Accepted pour les opérations async
                error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ {error_msg}")
                raise Exception(f"Erreur de traduction: {error_msg}")

            # Récupération de l'URL de statut
            translation_status_url = response.headers.get('Operation-Location')
            if not translation_status_url:
                raise Exception("URL de statut de traduction non trouvée dans la réponse")

            # Extraction de l'ID de traduction depuis l'URL
            translation_id = translation_status_url.split('/')[-1]

            logger.info("✅ Traduction démarrée avec succès")
            logger.info(f"🆔 Translation ID: {translation_id}")
            logger.info(f"📍 Status URL: {translation_status_url}")

            return translation_id

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur réseau lors du démarrage: {str(e)}")
            raise Exception(f"Erreur réseau: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage: {str(e)}")
            raise

    def check_translation_status(self, translation_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une traduction
        Version synchrone pour Azure Functions
        """
        try:
            # Construction de l'URL de statut
            status_url = f"{self.batch_api_url}/{translation_id}"

            # Headers pour la requête de statut
            status_headers = {
                'Ocp-Apim-Subscription-Key': self.trans_key
            }

            logger.info(f"🔍 Vérification statut traduction: {translation_id}")

            # Requête de statut
            response = requests.get(status_url, headers=status_headers, timeout=15)

            if response.status_code != 200:
                error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Erreur lors de la vérification: {error_msg}")
                return {
                    "status": "Failed",
                    "error": error_msg
                }

            # Analyse de la réponse
            status_data = response.json()
            api_status = status_data.get('status', 'Unknown')

            # Mapping des statuts Azure vers des statuts simplifiés
            status_mapping = {
                'NotStarted': 'Pending',
                'Running': 'InProgress',
                'Succeeded': 'Succeeded',
                'Failed': 'Failed',
                'Cancelled': 'Failed',
                'Cancelling': 'InProgress'
            }

            simplified_status = status_mapping.get(api_status, 'Unknown')

            # Informations détaillées
            result = {
                "status": simplified_status,
                "original_status": api_status,
                "progress": self._get_progress_info(status_data),
                "created_at": status_data.get('createdDateTimeUtc'),
                "last_updated": status_data.get('lastActionDateTimeUtc')
            }

            # Ajout des détails d'erreur si échec
            if simplified_status == 'Failed':
                result["error"] = self._extract_error_info(status_data)

            # Ajout des statistiques si disponibles
            if 'summary' in status_data:
                summary = status_data['summary']
                result["summary"] = {
                    "total": summary.get('total', 0),
                    "failed": summary.get('failed', 0),
                    "success": summary.get('success', 0),
                    "in_progress": summary.get('inProgress', 0)
                }

            logger.info(f"📊 Statut: {simplified_status} ({api_status})")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur réseau lors de la vérification: {str(e)}")
            return {
                "status": "Failed",
                "error": f"Erreur réseau: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification: {str(e)}")
            return {
                "status": "Failed",
                "error": f"Erreur interne: {str(e)}"
            }

    def cancel_translation(self, translation_id: str) -> bool:
        """Annule une traduction en cours"""
        try:
            cancel_url = f"{self.batch_api_url}/{translation_id}"

            response = requests.delete(
                cancel_url,
                headers={'Ocp-Apim-Subscription-Key': self.trans_key},
                timeout=15
            )

            if response.status_code in [200, 204]:
                logger.info(f"✅ Traduction {translation_id} annulée")
                return True
            else:
                logger.error(f"❌ Erreur lors de l'annulation: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'annulation: {str(e)}")
            return False

    def _get_progress_info(self, status_data: Dict[str, Any]) -> str:
        """Extrait les informations de progression"""
        if 'summary' in status_data:
            summary = status_data['summary']
            total = summary.get('total', 0)
            success = summary.get('success', 0)
            failed = summary.get('failed', 0)
            in_progress = summary.get('inProgress', 0)

            if total > 0:
                completed = success + failed
                percentage = (completed / total) * 100
                return f"Progression: {completed}/{total} ({percentage:.1f}%)"

        return status_data.get('status', 'En cours...')

    def _extract_error_info(self, status_data: Dict[str, Any]) -> str:
        """Extrait les informations d'erreur détaillées"""
        # Vérification des erreurs dans le summary
        if 'summary' in status_data and status_data['summary'].get('failed', 0) > 0:
            return "Échec de la traduction. Vérifiez le format du fichier et la langue cible."

        # Vérification des erreurs dans les détails
        if 'error' in status_data:
            error = status_data['error']
            if isinstance(error, dict):
                return error.get('message', 'Erreur inconnue')
            return str(error)

        return "Traduction échouée pour une raison inconnue"