import json
import importlib
import azure.functions as func
from unittest.mock import patch

cancel_translation = importlib.import_module("cancel_translation.__init__")


def make_request(route_id=None, query_id=None, method='DELETE'):
    return func.HttpRequest(
        method=method,
        url='/api/cancel_translation',
        headers={},
        params={} if query_id is None else {'translation_id': query_id},
        route_params={} if route_id is None else {'translation_id': route_id},
        body=b''
    )


@patch('cancel_translation.__init__.TranslationHandler')
def test_cancel_translation_success(handler_cls):
    handler = handler_cls.return_value
    handler.cancel_translation.return_value = {
        'success': True,
        'message': 'Traduction annulée'
    }

    req = make_request(route_id='123')
    resp = cancel_translation.main(req)

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body['data']['translation_id'] == '123'
    assert body['data']['message'] == 'Traduction annulée'
    handler.cancel_translation.assert_called_once_with('123')


@patch('cancel_translation.__init__.TranslationHandler')
def test_cancel_translation_missing_id(handler_cls):
    req = make_request()
    resp = cancel_translation.main(req)

    assert resp.status_code == 400
    body = json.loads(resp.get_body())
    assert body['success'] is False
    assert 'ID de traduction manquant' in body['error']['message']
