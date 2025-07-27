"""
Service de gestion des blobs Azure Storage pour Azure Functions
Adapté du code conteneur existant
"""

import logging
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from shared.config import Config

logger = logging.getLogger(__name__)


class BlobService:
    """Service pour la gestion des blobs Azure Storage"""
    container_name = Config.INPUT_CONTAINER

    def __init__(self):
        # Configuration Azure Storage
        self.account_name = Config.AZURE_ACCOUNT_NAME
        self.account_key = Config.AZURE_ACCOUNT_KEY

        if not self.account_name:
            raise ValueError("AZURE_ACCOUNT_NAME environnement variable manquante")
        if not self.account_key:
            raise ValueError("AZURE_ACCOUNT_KEY environnement variable manquante")

        # Assurer le format correct de la clé
        if not self.account_key.endswith("=="):
            self.account_key += "=="

        # Noms des conteneurs
        self.input_container = Config.INPUT_CONTAINER
        self.output_container = Config.OUTPUT_CONTAINER

        # Client Blob Storage
        self.blob_service_client = BlobServiceClient(
            account_url=Config.get_storage_url(),
            credential=self.account_key
        )

        logger.info("✅ BlobService initialisé")

    def prepare_blobs(self, file_content_base64: str, file_name: str, target_language: str) -> Dict[str, str]:
        """
        Prépare les blobs source et cible pour la traduction
        Version synchrone pour Azure Functions
        """
        logger.info(f"📁 Préparation des blobs pour {file_name} → {target_language}")

        try:
            # Génération des noms de fichiers avec suffixe de langue
            # Utilisation du nom de fichier fourni pour le blob source
            input_blob_name = file_name
            file_base, file_ext = input_blob_name.rsplit(".", 1) if "." in input_blob_name else (input_blob_name, "")

            # Format amélioré: file_name-fr.docx au lieu de file_name_fr.docx
            output_blob_name = f"{file_base}-{target_language}.{file_ext}" if file_ext else f"{file_base}-{target_language}"

            logger.info(f"📄 Fichier source: {input_blob_name}")
            logger.info(f"📄 Fichier cible: {output_blob_name}")

            # Nettoyage des anciens fichiers (>1h)
            self._delete_old_files(self.output_container, max_age_hours=1)

            # Suppression du fichier cible s'il existe déjà
            self._check_and_delete_target_blob(self.output_container, output_blob_name)

            # Conversion et upload du fichier source
            file_content_binary = base64.b64decode(file_content_base64)
            file_size = len(file_content_binary)

            logger.info(f"📊 Taille du fichier: {file_size / 1024:.1f} KB")

            # Upload du fichier source
            input_blob_client = self.blob_service_client.get_blob_client(
                container=self.input_container,
                blob=input_blob_name
            )

            input_blob_client.upload_blob(
                file_content_binary,
                overwrite=True,
                content_type=self._get_content_type(file_name)
            )

            logger.info("✅ Fichier source uploadé avec succès")

            # Génération des URLs SAS
            source_url = self._generate_sas_url(self.input_container, input_blob_name, read=True)
            target_url = self._generate_sas_url(self.output_container, output_blob_name, write=True)

            return {
                "source_url": source_url,
                "target_url": target_url,
                "input_blob_name": input_blob_name,
                "output_blob_name": output_blob_name
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de la préparation des blobs: {str(e)}")
            raise

    def get_translated_file_url(self, output_blob_name: str) -> Optional[str]:
        """
        Génère une URL de téléchargement pour le fichier traduit
        """
        try:
            # Vérifier si le blob existe
            blob_client = self.blob_service_client.get_blob_client(
                container=self.output_container,
                blob=output_blob_name
            )

            if not blob_client.exists():
                logger.warning(f"⚠️ Fichier traduit introuvable: {output_blob_name}")
                return None

            # Générer URL SAS avec permissions de écriture (valide 24h)
            download_url = self._generate_sas_url(
                self.output_container, 
                output_blob_name, 
                write=True,
                expiry_hours=24
            )

            logger.info(f"✅ URL de téléchargement générée pour: {output_blob_name}")
            return download_url

        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de l'URL: {str(e)}")
            return None

    def download_translated_file(self, output_blob_name: str) -> Optional[bytes]:
        """
        Télécharge le contenu du fichier traduit
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.output_container,
                blob=output_blob_name
            )

            if not blob_client.exists():
                logger.warning(f"⚠️ Fichier traduit introuvable: {output_blob_name}")
                return None

            # Téléchargement du contenu
            blob_data = blob_client.download_blob()
            content = blob_data.readall()

            logger.info(f"✅ Fichier téléchargé: {len(content)} bytes")
            return content

        except Exception as e:
            logger.error(f"❌ Erreur lors du téléchargement: {str(e)}")
            return None

    def cleanup_translation_files(self, input_blob_name: str, output_blob_name: str) -> bool:
        """
        Nettoie les fichiers de traduction après traitement
        """
        try:
            success = True

            # Suppression du fichier source
            try:
                input_blob_client = self.blob_service_client.get_blob_client(
                    container=self.input_container,
                    blob=input_blob_name
                )
                input_blob_client.delete_blob()
                logger.info(f"🗑️ Fichier source supprimé: {input_blob_name}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer le fichier source: {str(e)}")
                success = False

            # Suppression du fichier cible (optionnel)
            try:
                output_blob_client = self.blob_service_client.get_blob_client(
                    container=self.output_container,
                    blob=output_blob_name
                )
                if output_blob_client.exists():
                    output_blob_client.delete_blob()
                    logger.info(f"🗑️ Fichier cible supprimé: {output_blob_name}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer le fichier cible: {str(e)}")

            return success

        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
            return False

    def _generate_sas_url(self, container_name: str, blob_name: str, 
                      read: bool = False, write: bool = False, 
                      expiry_hours: int = 2) -> str:
        """Génère une URL SAS pour un blob"""
        # Crée l'objet permission directement
        if write == True:
            permissions="rw"
        else:
            permissions="r"
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=permissions,
            expiry=expiry_time
        )
        logger.info(f"SAS URL générée: {Config.get_storage_url()}/{container_name}/{blob_name}?{sas_token}")
        return f"{Config.get_storage_url()}/{container_name}/{blob_name}?{sas_token}"

    def _get_content_type(self, file_name: str) -> str:
        """Détermine le type MIME d'un fichier"""
        extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'ppt': 'application/vnd.ms-powerpoint',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'txt': 'text/plain',
            'html': 'text/html',
            'htm': 'text/html',
            'xml': 'application/xml',
            'rtf': 'application/rtf'
        }
        
        return content_types.get(extension, 'application/octet-stream')

    def _check_and_delete_target_blob(self, container_name: str, blob_name: str) -> bool:
        """Vérifie et supprime un blob cible s'il existe"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            if blob_client.exists():
                blob_client.delete_blob()
                logger.info(f"🗑️ Ancien fichier cible supprimé: {blob_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la suppression du fichier cible: {str(e)}")
            return False

    def _delete_old_files(self, container_name: str, max_age_hours: int = 1) -> int:
        """Supprime les anciens fichiers du conteneur"""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            deleted_count = 0

            blobs = container_client.list_blobs()
            for blob in blobs:
                if blob.last_modified < cutoff_time:
                    try:
                        container_client.delete_blob(blob.name)
                        deleted_count += 1
                        logger.debug(f"🗑️ Ancien fichier supprimé: {blob.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de supprimer {blob.name}: {str(e)}")

            if deleted_count > 0:
                logger.info(f"🧹 {deleted_count} anciens fichiers supprimés du conteneur {container_name}")

            return deleted_count

        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage des anciens fichiers: {str(e)}")
            return 0
        
    def check_blob_exists(self, blob_name: str) -> bool:
        """Vérifie si un blob existe dans un container"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return blob_client.exists()
        except Exception as e:
            logger.error(
                f"Erreur lors de la vérification du blob {blob_name}: {str(e)}")
            return False
        
    def prepare_translation_urls(self, input_blob_name: str, target_language: str) -> Dict[str, str]:
        """
        Prépare les URLs pour la traduction d'un blob existant
        Le fichier source est déjà dans le container doc-to-trad
        """

        logger.info(
            f"🔄 Préparation des URLs pour {input_blob_name} → {target_language}")

        try:
            # Génération du nom du fichier de sortie à partir du nom normalisé
            file_base, file_ext = input_blob_name.rsplit(
                ".", 1) if "." in input_blob_name else (input_blob_name, "")

            # Format: file_name-fr.docx avec limitation de longueur
            lang_suffix = f"-{target_language}"

            # Calculer la longueur maximale pour le nom de base
            max_total_length = 200  # Limite conservatrice
            extension_length = len(f".{file_ext}") if file_ext else 0
            suffix_length = len(lang_suffix)
            max_base_length = max_total_length - extension_length - suffix_length

            # Tronquer le nom de base si nécessaire
            if len(file_base) > max_base_length:
                file_base = file_base[:max_base_length]
                logger.warning(
                    f"⚠️ Nom de fichier de base tronqué pour éviter la limite Azure: {len(file_base)} caractères")

            output_blob_name = f"{file_base}{lang_suffix}.{file_ext}" if file_ext else f"{file_base}{lang_suffix}"

            logger.info(f"📄 Fichier source: {input_blob_name}")
            logger.info(f"📝 Fichier source normalisé: {input_blob_name}")
            logger.info(f"📄 Fichier cible: {output_blob_name}")
            logger.info(
                f"📏 Longueur du nom de fichier cible: {len(output_blob_name)} caractères")

            # Nettoyage des anciens fichiers (>1h)
            self._delete_old_files(self.output_container, max_age_hours=1)

            # Suppression du fichier cible s'il existe déjà
            self._check_and_delete_target_blob(self.output_container, output_blob_name)

            # Génération des SAS URLs
            source_url = self._generate_sas_url(
                self.input_container, input_blob_name, read=True)
            target_url = self._generate_sas_url(
                self.output_container, output_blob_name, write=True)

            logger.info("✅ URLs SAS générées")

            return {
                "source_url": source_url,
                "target_url": target_url,
                "input_blob_name": input_blob_name,
                "output_blob_name": output_blob_name,
                "original_file_name": input_blob_name
            }

        except Exception as e:
            logger.error(f"Erreur lors de la préparation des URLs: {str(e)}")
            raise