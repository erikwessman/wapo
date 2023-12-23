import os
import pytest
from src.token_api import TokenAPI


@pytest.fixture(scope="function")
def token_api():
    token_json_path = "test/data/tokens.json"
    token_api = TokenAPI(token_json_path)

    yield token_api

    os.remove(token_json_path)


def test_set_tokens(token_api):
    token_api.set_tokens(123, 10)
    tokens = token_api.get_tokens(123)
    assert tokens == 10


def test_update_tokens(token_api):
    token_api.update_tokens(123, 10)
    token_api.update_tokens(123, 10)
    tokens = token_api.get_tokens(123)
    assert tokens == 20
