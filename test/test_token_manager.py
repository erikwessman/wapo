import os
import pytest
from src.managers import TokenManager


@pytest.fixture(scope="function")
def token_manager():
    token_json_path = "test/data/tokens.json"
    token_manager = TokenManager(token_json_path)

    yield token_manager

    os.remove(token_json_path)


def test_set_tokens(token_manager):
    token_manager.set_tokens(123, 10)
    tokens = token_manager.get_tokens(123)
    assert tokens == 10


def test_update_tokens(token_manager):
    token_manager.update_tokens(123, 10)
    token_manager.update_tokens(123, 10)
    tokens = token_manager.get_tokens(123)
    assert tokens == 20
