import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.routers.player_routers import router
from app.schemas.player_schemas import PlayerIn, PlayerOut
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.models.player_models import Player as PlayerModel
from fastapi import HTTPException

@pytest.fixture
def match_data():
    return {
        "match_name": "test_match",
        "max_players": 4,
        "host": 1,
        "match_id": 1
    }

def test_create_player(player_data):
    expected_response = {
        **player_data,
        "operation_result": "Player created successfully"
    }