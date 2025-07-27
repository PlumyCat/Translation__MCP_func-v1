import json
import azure.functions as func
import pytest

from shared.utils import response_helper as rh


def make_request(method='POST', url='/api/test', body=None, headers=None):
    body_bytes = json.dumps(body).encode() if body is not None else b''
    return func.HttpRequest(method=method, url=url, headers=headers or {}, params={}, route_params={}, body=body_bytes)


def test_create_response():
    resp = rh.create_response({'foo': 'bar'}, 201)
    assert resp.status_code == 201
    data = json.loads(resp.get_body())
    assert data['success'] is True
    assert data['data']['foo'] == 'bar'


def test_create_error_response():
    resp = rh.create_error_response('bad', 400)
    assert resp.status_code == 400
    data = json.loads(resp.get_body())
    assert data['success'] is False
    assert data['error']['message'] == 'bad'


def test_validate_json_request_success():
    req = make_request(body={'name': 'test', 'value': 1})
    ok, data = rh.validate_json_request(req, ['name', 'value'])
    assert ok is True
    assert data['name'] == 'test'


def test_validate_json_request_missing_fields():
    req = make_request(body={'name': 'test'})
    ok, resp = rh.validate_json_request(req, ['name', 'value'])
    assert ok is False
    body = json.loads(resp.get_body())
    assert body['error']['code'] == 'MISSING_FIELDS'


def test_extract_user_id_from_header():
    req = make_request(headers={'X-User-ID': 'abc'})
    assert rh.extract_user_id(req) == 'abc'


def test_extract_user_id_from_body():
    req = make_request(body={'user_id': 'xyz'})
    assert rh.extract_user_id(req) == 'xyz'


def test_format_file_size():
    assert rh.format_file_size(0) == '0 B'
    assert rh.format_file_size(1024) == '1.0 KB'


def test_format_duration():
    assert rh.format_duration(30) == '30.0s'
    assert rh.format_duration(120) == '2.0min'
    assert rh.format_duration(7200) == '2.0h'
