from unittest.mock import patch
from shared.services.translation_handler import TranslationHandler
from shared.models.schemas import TranslationStatus


@patch('shared.services.translation_handler.BlobService')
@patch('shared.services.translation_handler.TranslationService')
@patch('shared.services.translation_handler.StateManager')
def test_validate_request_success(state_cls, trans_cls, blob_cls):
    # instantiate without executing original __init__ using patch
    handler = TranslationHandler()
    errors = handler._validate_request('YmFzZTY0', 'file.pdf', 'fr', 'user1')
    assert errors == []


@patch('shared.services.translation_handler.BlobService')
@patch('shared.services.translation_handler.TranslationService')
@patch('shared.services.translation_handler.StateManager')
def test_validate_request_errors(state_cls, trans_cls, blob_cls):
    handler = TranslationHandler()
    errors = handler._validate_request('', 'file.xyz', 'zz', '')
    assert 'Missing file content' in errors
    assert any('Unsupported file format' in e for e in errors)
    assert any('Unsupported language code' in e for e in errors)
    assert 'Missing user ID' in errors
