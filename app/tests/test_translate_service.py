# import pytest
# from unittest.mock import patch, MagicMock, Mock
# from app.services.translate import TranslateService
# from google.cloud import translate_v2 as translate
# from flask import Flask 
# from app.main import create_app

# secret_key_mock = "f19a51f6df5b7fa6e0c01e29f146343e596a7899ae3a8f5bd241b0fc6a26abd7"


# class TestConfig:
#     TESTING = True

# @pytest.fixture
# def app():
#     app = create_app(TestConfig)
#     app.config['SECRET_KEY'] = secret_key_mock
#     return app

# @pytest.fixture
# def app_context(app):
#     with app.app_context():
#         yield 

# def test_translate_fields_basic():
#     with patch('app.services.translate.translate.Client', autospec=True) as mock_translate_client_constructor:
#         mock_translate_client = MagicMock()
#         mock_translate_client.translate.return_value = [
#             {'translatedText': 'ola!'},
#             {'translatedText': 'espero que isso nao quebre o deploy'},
#             {'translatedText': 'testando.'},
#             {'translatedText': 'testando'}
#         ]
#         mock_translate_client_constructor.return_value = mock_translate_client

#         translate_service = TranslateService()

#         data = {
#             "Title": "hi!",
#             "Description": "hope it doesnt break the deploy", 
#             "Keywords": ["testing.", "testing"]
#         }

#         result = translate_service.translate_fields(data, desired_fields=["Title", "Description", "Keywords"])

#         assert result["Title"] == "ola!"
#         assert result["Description"] == "espero que isso nao quebre o deploy"
#         assert result["Keywords"] == ["testando.", "testando"]

# def test_translate_fields_nested():
#     with patch('app.services.translate.translate.Client', autospec = True) as mock_translate_client_constructor:
#         mock_translate_client = MagicMock()
#         mock_translate_client.translate.return_value = [
#             {'translatedText': 'titulo aninhado'},
#             {'translatedText': 'descricao aninhada'}, 
#             {'translatedText': 'palavra-chave1'},
#             {'translatedText': 'palavra-chave2'}
#         ]
#         mock_translate_client_constructor.return_value = mock_translate_client

#         translate_service = TranslateService()

#         data = {
#             "Title": "nested title",
#             "Content": {
#                 "Description": "nested description",
#                 "Keywords": ["keyword1", "keyword2"]
#             }
#         }

#         result = translate_service.translate_fields(data, desired_fields=["Title", "Description", "Keywords", "Content"])

#         assert result["Title"] == "titulo aninhado"
#         assert result["Content"]["Description"] == "descricao aninhada"
#         assert result["Content"]["Keywords"] == ["palavra-chave1", "palavra-chave2"]

# def test_translate_fields_no_desired_fields():
#     with patch('app.services.translate.translate.Client', autospec=True) as mock_translate_client_constructor:
#         mock_translate_client = MagicMock()
#         mock_translate_client_constructor.return_value = mock_translate_client

#         translate_service = TranslateService()

#         data = {
#             "Title": "hello word",
#             "Description": "dont translate me",
#         }

#         result = translate_service.translate_fields(data, desired_fields=[])

#         mock_translate_client.translate.assert_not_called()
#         assert result == data

# def test_translate_fields_exception(app_context):
#     with patch('app.services.translate.translate.Client', autospec=True) as mock_translate_client_constructor:
#         mock_translate_client = MagicMock()
#         mock_translate_client.translate.side_effect = Exception("Translation error")
#         mock_translate_client_constructor.return_value = mock_translate_client

#         translate_service = TranslateService()

#         data = {
#             "Title": "hello world"
#         }

#         result = translate_service.translate_fields(data)

#         assert result == data