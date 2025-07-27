import time
from shared.services.state_manager import StateManager
from shared.models.schemas import TranslationInfo, BlobUrls, TranslationStatus


def make_info(uid='user', status=TranslationStatus.IN_PROGRESS.value, started=None):
    return TranslationInfo(
        file_name='file.pdf',
        target_language='fr',
        user_id=uid,
        blob_urls=BlobUrls(
            source_url='s', target_url='t', input_blob_name='i', output_blob_name='o'
        ),
        status=status,
        started_at=started if started is not None else time.time(),
        translation_id='azure-id'
    )


def test_save_get_delete_state():
    sm = StateManager()
    info = make_info()
    sm.save_translation_state('1', info)
    assert sm.get_translation_state('1') == info
    sm.delete_translation_state('1')
    assert sm.get_translation_state('1') is None


def test_count_active_translations():
    sm = StateManager()
    sm._translations.clear()
    sm.save_translation_state('1', make_info(uid='u1'))
    sm.save_translation_state('2', make_info(uid='u1', status=TranslationStatus.SUCCEEDED.value))
    sm.save_translation_state('3', make_info(uid='u2'))
    assert sm.count_active_translations('u1') == 1


def test_cleanup_old_translations():
    sm = StateManager()
    sm._translations.clear()
    old_time = time.time() - 7200
    sm.save_translation_state('old', make_info(started=old_time))
    sm.save_translation_state('new', make_info())
    removed = sm.cleanup_old_translations(max_age_hours=1)
    assert removed == 1
    assert 'old' not in sm._translations
