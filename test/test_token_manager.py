import os
import pytest
from src.managers import PlayerManager


@pytest.fixture(scope="function")
def player_manager():
    token_json_path = "test/data/tokens.json"
    player_manager = PlayerManager(token_json_path)

    yield player_manager

    os.remove(token_json_path)


def test_set_tokens(player_manager):
    player_manager.set_tokens(123, 10)
    tokens = player_manager.get_tokens(123)
    assert tokens == 10


def test_update_tokens(player_manager):
    player_manager.update_tokens(123, 10)
    player_manager.update_tokens(123, 10)
    tokens = player_manager.get_tokens(123)
    assert tokens == 20
