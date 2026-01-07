"""
Deployment Store
Stocke l'historique des deploiements dans Azure Table Storage
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, asdict

from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


@dataclass
class DeploymentRecord:
    """Enregistrement d'un deploiement"""
    client_name: str
    deployment_id: str
    region: str
    status: str  # Active, Failed, Deleted
    deployed_at: str
    resource_group: str
    storage_account: str
    translator_name: str
    function_app_name: str
    function_app_url: str
    function_key: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DeploymentRecord":
        return cls(**data)


class DeploymentStore:
    """
    Stockage des deploiements.
    Utilise Azure Blob Storage pour persister les donnees.
    """

    CONTAINER_NAME = "deployment-records"
    BLOB_NAME = "deployments.json"

    def __init__(self):
        """Initialise le store avec les credentials depuis les variables d'env"""
        connection_string = os.environ.get("AzureWebJobsStorage", "")

        if connection_string:
            self.blob_service = BlobServiceClient.from_connection_string(connection_string)
            self._ensure_container()
        else:
            self.blob_service = None
            logger.warning("No storage connection string found, using in-memory store")

        self._cache: List[DeploymentRecord] = []
        self._loaded = False

    def _ensure_container(self):
        """Cree le container s'il n'existe pas"""
        try:
            container_client = self.blob_service.get_container_client(self.CONTAINER_NAME)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            logger.error(f"Failed to ensure container: {e}")

    def _load(self):
        """Charge les donnees depuis le storage"""
        if self._loaded:
            return

        if not self.blob_service:
            self._loaded = True
            return

        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.CONTAINER_NAME,
                blob=self.BLOB_NAME
            )

            if blob_client.exists():
                data = blob_client.download_blob().readall()
                records = json.loads(data)
                self._cache = [DeploymentRecord.from_dict(r) for r in records]

            self._loaded = True
        except Exception as e:
            logger.error(f"Failed to load deployments: {e}")
            self._loaded = True

    def _save(self):
        """Sauvegarde les donnees dans le storage"""
        if not self.blob_service:
            return

        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.CONTAINER_NAME,
                blob=self.BLOB_NAME
            )

            data = json.dumps([r.to_dict() for r in self._cache])
            blob_client.upload_blob(data, overwrite=True)
        except Exception as e:
            logger.error(f"Failed to save deployments: {e}")

    def add(self, record: DeploymentRecord):
        """Ajoute un enregistrement de deploiement"""
        self._load()

        # Verifier si un deploiement existe deja pour ce client
        existing = next((r for r in self._cache if r.client_name == record.client_name), None)
        if existing:
            # Mettre a jour l'existant
            self._cache.remove(existing)

        self._cache.append(record)
        self._save()

    def get(self, client_name: str) -> Optional[DeploymentRecord]:
        """Recupere un deploiement par nom de client"""
        self._load()
        return next((r for r in self._cache if r.client_name == client_name), None)

    def list(self, region: Optional[str] = None, status: Optional[str] = None) -> List[DeploymentRecord]:
        """Liste les deploiements avec filtres optionnels"""
        self._load()

        results = self._cache

        if region:
            results = [r for r in results if r.region == region]

        if status:
            results = [r for r in results if r.status == status]

        # Trier par date de deploiement (plus recent en premier)
        results.sort(key=lambda r: r.deployed_at, reverse=True)

        return results

    def update_status(self, client_name: str, status: str):
        """Met a jour le statut d'un deploiement"""
        self._load()

        record = self.get(client_name)
        if record:
            record.status = status
            self._save()

    def delete(self, client_name: str):
        """Supprime un enregistrement de deploiement"""
        self._load()

        record = self.get(client_name)
        if record:
            self._cache.remove(record)
            self._save()


# Instance globale
_store: Optional[DeploymentStore] = None


def get_store() -> DeploymentStore:
    """Retourne l'instance globale du store"""
    global _store
    if _store is None:
        _store = DeploymentStore()
    return _store
