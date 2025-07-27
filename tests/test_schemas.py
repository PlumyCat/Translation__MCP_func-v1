import pytest
from shared.models import schemas


def test_supported_language_true():
    assert schemas.SupportedLanguages.is_supported('fr') is True


def test_supported_language_false():
    assert schemas.SupportedLanguages.is_supported('zz') is False


def test_get_language_name():
    assert schemas.SupportedLanguages.get_language_name('fr') == 'French'


def test_file_format_supported():
    assert schemas.FileFormats.is_supported('document.pdf') is True


def test_file_format_not_supported():
    assert schemas.FileFormats.is_supported('image.bmp') is False


def test_validate_file_format():
    assert schemas.validate_file_format('file.docx') is True
    assert schemas.validate_file_format('file.xyz') is False


def test_validate_language_code():
    assert schemas.validate_language_code('en') is True
    assert schemas.validate_language_code('zzz') is False


def test_get_file_extension():
    assert schemas.get_file_extension('file.txt') == '.txt'
    assert schemas.get_file_extension('file') == ''
