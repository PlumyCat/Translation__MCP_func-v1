"""
Service Microsoft Graph pour OneDrive
Adapté du code conteneur existant
"""

import logging
import requests
import base64
from typing import Dict, Any, Optional
from shared.config import Config

logger = logging.getLogger(__name__)


class GraphService:
    """Service pour l'intégration Microsoft Graph (OneDrive)"""

    def __init__(self):
        self.client_id = Config.CLIENT_ID
        self.client_secret = Config.CLIENT_SECRET
        self.tenant_id = Config.TENANT_ID
        self.onedrive_upload_enabled = Config.ONEDRIVE_UPLOAD_ENABLED
        self.onedrive_folder = Config.ONEDRIVE_FOLDER or "Translated Documents"

        # URLs Microsoft Graph
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_base_url = "https://graph.microsoft.com/v1.0"

        # Cache du token (en production, utiliser Redis ou équivalent)
        self._access_token = None
        self._token_expires_at = None

        logger.info("✅ GraphService initialisé")

    def is_configured(self) -> bool:
        """Vérifie si le service Graph est configuré"""
        return Config.is_onedrive_enabled()

    def upload_to_onedrive(self, file_content: bytes, file_name: str, user_id: str) -> Dict[str, Any]:
        """
        Upload un fichier vers OneDrive
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "OneDrive non configuré"
            }
        if self.onedrive_upload_enabled is False:
            return {
                "success": True,
                "info": "Upload OneDrive désactivé"
            }
        try:
            logger.info(f"☁️ Upload vers OneDrive: {file_name} pour {user_id}")

            # Obtention du token d'accès
            access_token = self._get_access_token()
            if not access_token:
                return {
                    "success": False,
                    "error": "Impossible d'obtenir le token d'accès Microsoft Graph"
                }

            # Upload vers OneDrive avec le nom de fichier original
            upload_url = f"{self.graph_base_url}/users/{user_id}/drive/root:/{self.onedrive_folder}/{file_name}:/content"
            logger.info(f"📤 URL d'upload OneDrive: {upload_url}")

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            response = requests.put(
                upload_url,
                headers=headers,
                data=file_content,
                timeout=60
            )

            if response.status_code in [200, 201]:
                file_info = response.json()
                onedrive_url = file_info.get('webUrl')

                logger.info(f"✅ Fichier uploadé vers OneDrive: {file_name}")
                return {
                    "success": True,
                    "onedrive_url": onedrive_url,
                    "file_id": file_info.get('id'),
                    "file_name": file_name
                }
            else:
                error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Erreur upload OneDrive: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'upload OneDrive: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur interne: {str(e)}"
            }

    def _get_access_token(self) -> Optional[str]:
        """Obtient un token d'accès Microsoft Graph"""
        try:
            logger.info(f"🔑 Demande de token Microsoft Graph...")
            logger.info(
                f"   Client ID: {self.client_id[:8] if self.client_id else 'None'}...")
            logger.info(
                f"   Tenant ID: {self.tenant_id[:8] if self.tenant_id else 'None'}...")
            logger.info(f"   Token URL: {self.token_url}")

            # Vérifier si le token en cache est encore valide
            if self._access_token and self._token_expires_at:
                import time
                if time.time() < self._token_expires_at - 300:  # 5 min de marge
                    logger.info("✅ Token en cache encore valide")
                    return self._access_token

            # Demande d'un nouveau token
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }

            logger.info(f"📤 Requête token vers: {self.token_url}")
            response = requests.post(self.token_url, data=data, timeout=30)
            logger.info(f"📥 Réponse token - Status: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                logger.info(
                    f"✅ Token obtenu avec succès (expire dans {expires_in}s)")

                import time
                self._token_expires_at = time.time() + expires_in

                logger.info("✅ Token Microsoft Graph obtenu")
                return self._access_token
            else:
                error_text = response.text[:200]  # Limiter la longueur
                logger.error(
                    f"❌ Erreur obtention token: {response.status_code}")
                logger.error(f"   Détails: {error_text}")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'obtention du token: {str(e)}")
            return None
