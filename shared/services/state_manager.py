import logging
import threading
import time
from typing import Dict, Optional

from shared.models.schemas import TranslationInfo, TranslationStatus

logger = logging.getLogger(__name__)


class StateManager:
    """Simple gestionnaire d'état en mémoire."""

    _lock = threading.Lock()
    _translations: Dict[str, TranslationInfo] = {}

    def save_translation_state(self, translation_id: str, info: TranslationInfo) -> bool:
        """Enregistre ou met à jour l'état d'une traduction."""
        with self._lock:
            self._translations[translation_id] = info
        logger.debug(f"State saved for {translation_id}")
        return True

    def get_translation_state(self, translation_id: str) -> Optional[TranslationInfo]:
        """Récupère l'état d'une traduction."""
        with self._lock:
            return self._translations.get(translation_id)

    def delete_translation_state(self, translation_id: str, delay_minutes: int = 0) -> bool:
        """Supprime l'état d'une traduction."""
        # Ignorer le délai pour cette implémentation simple
        with self._lock:
            if translation_id in self._translations:
                del self._translations[translation_id]
                logger.debug(f"State deleted for {translation_id}")
                return True
        return False

    def count_active_translations(self, user_id: str) -> int:
        """Compte les traductions en cours pour un utilisateur."""
        with self._lock:
            return sum(
                1
                for info in self._translations.values()
                if info.user_id == user_id and info.status == TranslationStatus.IN_PROGRESS.value
            )

    def cleanup_old_translations(self, max_age_hours: int = 2) -> int:
        """Supprime les traductions plus anciennes que ``max_age_hours``."""
        cutoff = time.time() - (max_age_hours * 3600)
        to_delete = []
        with self._lock:
            for tid, info in self._translations.items():
                if info.started_at < cutoff:
                    to_delete.append(tid)
            for tid in to_delete:
                del self._translations[tid]
        if to_delete:
            logger.debug(f"Cleaned up {len(to_delete)} old translations")
        return len(to_delete)
