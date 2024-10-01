import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.routers.player_routers import router
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository


client = TestClient(router)

@pytest.fixture
def player_data():
    return {
        "username": "test_player",
        "player_id": 1
    }

def test_create_player(player_data):
    expected_response = {
        **player_data,
        "operation_result": "Player created successfully"
    }
    with patch.object(PlayerRepository, 'create_player', return_value=MagicMock(**expected_response)):
        response = client.post("/players/", json={"username": player_data["username"]})
        assert response.status_code == 201
        assert response.json() == expected_response

def test_get_player(player_data):
    expected_response = {
        **player_data,
        "operation_result": "Player found successfully"
    }
    with patch.object(PlayerRepository, 'get_player', return_value=MagicMock(**expected_response)):
        response = client.get(f"/players/{player_data['player_id']}")
        assert response.status_code == 200
        assert response.json() == expected_response

def test_get_player_not_found():
    with patch.object(PlayerRepository, 'get_player', side_effect=HTTPException(status_code=404, detail="Player not found.")):
        with pytest.raises(HTTPException) as exc_info:
            response = client.get("/players/999")
            assert response.status_code == 404
            assert exc_info.value.detail == {"detail": "Match not found."}
        
def test_assign_match_to_player():
    match_id = 1
    player_list = []
    with patch.object(PlayerRepository, 'assign_match_to_player', return_value="success"):
        with patch.object(MatchRepository, 'get_player_ids_in_match', return_value=player_list):
            with patch.object(PlayerRepository, 'get_player', return_value=MagicMock(player_id=1)):
                response = client.put("/players/1/AssignToMatch/1")
                assert response.status_code == 204

def test_assign_match_to_player_match_not_found():
    with patch.object(PlayerRepository, 'assign_match_to_player', return_value="match not found"):
        with patch.object(MatchRepository, 'get_player_ids_in_match', return_value=None):
            with patch.object(PlayerRepository, 'get_player', return_value=MagicMock(player_id=1)):
                with pytest.raises(HTTPException) as exc_info:
                    response = client.put("/players/1/AssignToMatch/999")
                    assert response.status_code == 404
                    assert exc_info.value.detail == "Match not found."

def test_unassign_match_to_player():
    with patch.object(PlayerRepository, 'unassign_match_to_player', return_value="success"):
        response = client.put("/players/1/UnassignMatch")
        assert response.status_code == 204

def test_unassign_match_to_player_not_found():
    with patch.object(PlayerRepository, 'unassign_match_to_player', return_value="Player not belong to any match"):
        with pytest.raises(HTTPException) as exc_info:
            response = client.put("/players/1/UnassignMatch")
            assert response.status_code == 404
            assert exc_info.value.detail == {"detail": "Match not found."}

def test_delete_player():
    with patch.object(PlayerRepository, 'delete_player', return_value=True):
        response = client.delete("/players/1")
        assert response.status_code == 204

def test_delete_player_not_found():
    with patch.object(PlayerRepository, 'delete_player', return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            response = client.delete("/players/999")
            assert response.status_code == 404
            assert exc_info.value.detail == {"detail": "Player not found."}