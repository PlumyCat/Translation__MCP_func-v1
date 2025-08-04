import json
import importlib
import azure.functions as func
from unittest.mock import patch

start_translation = importlib.import_module("start_translation.__init__")


def make_request(body=None, method='POST'):
    body_bytes = json.dumps(body).encode() if body is not None else b''
    return func.HttpRequest(
        method=method,
        url='/api/start_translation',
        headers={},
        params={},
        route_params={},
        body=body_bytes,
    )


@patch('start_translation.__init__.TranslationHandler')
def test_start_translation_success(handler_cls):
    handler = handler_cls.return_value
    handler.start_translation.return_value = {
        'success': True,
        'message': 'ok',
        'data': {
            'translation_id': '123',
            'azure_translation_id': 'az-456',
            'status': 'En cours'
        }
    }

    req = make_request({
        'file_content': 'YmFzZTY0',
        'file_name': 'doc.txt',
        'target_language': 'fr',
        'user_id': 'user1'
    })

    resp = start_translation.main(req)
    assert resp.status_code == 202
    body = json.loads(resp.get_body())
    assert body['data']['translation_id'] == '123'
    assert body['data']['azure_translation_id'] == 'az-456'
    assert body['data']['status'] == 'En cours'
    handler.start_translation.assert_called_once_with(
        file_content='YmFzZTY0',
        file_name='doc.txt',
        target_language='fr',
        user_id='user1'
    )


@patch('start_translation.__init__.TranslationHandler')
def test_start_translation_missing_fields(handler_cls):
    req = make_request({'file_content': 'abc', 'file_name': 'doc.txt'})
    resp = start_translation.main(req)
    assert resp.status_code == 400
    body = json.loads(resp.get_body())
    assert body['success'] is False
    assert 'Champs manquants' in body['error']['message']
