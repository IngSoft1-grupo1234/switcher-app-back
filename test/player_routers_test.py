import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.routers.player_routers import router
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel



client = TestClient(router)

@pytest.fixture
def mock_session():
    with patch('app.database.session', autospec=True) as mock_session:
        yield mock_session

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
        
def test_assign_match_to_player(player_data):
    expected_response = {
        **player_data,
        "operation_result": "Player found successfully"
    }

    player = PlayerModel(player_id=1, match_id=1)
    player_list = []
    with patch.object(PlayerRepository, 'assign_match_to_player', return_value=None),\
            patch.object(MatchRepository, 'get_player_ids_in_match', return_value=player_list),\
            patch.object(PlayerRepository, 'get_player', return_value=player):
                response = client.put("/players/1/AssignToMatch/1")
                assert response.status_code == 204

def test_assign_match_to_player_match_not_found(player_data):
    player = PlayerModel(player_id=1, match_id=None)

    with patch.object(PlayerRepository, 'get_player', return_value=player),\
            patch.object(PlayerRepository, 'assign_match_to_player', side_effect=HTTPException(status_code=404, detail="Match not found.")):
            with pytest.raises(HTTPException) as exc_info:
                response = client.put("/players/1/AssignToMatch/999")
                assert response.status_code == 404
                assert exc_info.value.detail == "Match not found."



def test_unassign_match_to_player_not_found(mock_session):
    mock_db = mock_session.return_value
    mock_db.close = MagicMock()
    
    with patch('app.crud.player_crud.PlayerRepository.get_player', side_effect=HTTPException(status_code=404, detail="Player not found.")),\
            patch.object(PlayerRepository, 'unassign_match_to_player', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            response = client.put("/players/999/UnassignMatch")
            assert response.status_code == 404
            assert exc_info.value.detail == "Player not found."

def test_delete_player():
    with patch.object(PlayerRepository, 'delete_player', return_value=True):
        response = client.delete("/players/1")
        assert response.status_code == 204

def test_delete_player_not_found(mock_session):
    mock_db = mock_session.return_value
    mock_db.close = MagicMock()
        
    with patch('app.crud.player_crud.PlayerRepository.delete_player', side_effect=HTTPException(status_code=404, detail="Player not found.")):
        with pytest.raises(HTTPException) as exc_info:
            response = client.delete("/players/999")
            assert response.status_code == 404
            assert exc_info.value.detail == "Player not found."


def test_use_shape_card():
    with patch.object(PlayerRepository, 'use_shape_card', return_value=([], {}, "")),\
         patch.object(PlayerRepository, 'get_player', return_value=MagicMock(player_id=1)),\
         patch.object(MatchRepository, 'get_match'  , return_value=MagicMock(match_id=1)),\
         patch.object(ShapeCardRepository, 'get_shape_card', return_value=MagicMock(shape_card_id=1, shape_card_type=MagicMock(value="type"), player_id=1)),\
         patch.object(PlayerRepository, 'winner_without_shape_card', return_value=None):
        response = client.put("/players/use_shape_card/1", json={"color":"r", "location":"(1,1)"})
        assert response.status_code == 204

# patch('app.websocket.connection_manager.ConnectionManager.broadcast_to_id_list', new_callable=AsyncMock),\
    #    patch('app.crud.player_crud.PlayerRepository.broadcast_message_to_id_list', new_callable=AsyncMock)
def test_use_shape_card_not_found():
    with patch.object(PlayerRepository, 'use_shape_card', side_effect=HTTPException(status_code=404, detail="Shape card not found.")),\
         patch.object(ShapeCardRepository, 'get_shape_card', side_effect=HTTPException(status_code=404, detail="Shape card not found.")),\
         patch.object(PlayerRepository, 'winner_without_shape_card', return_value=None):
         with pytest.raises(HTTPException) as exc_info:
            response = client.put("/players/use_shape_card/999", json={"color":"r", "location":"(1,1)"})
            assert response.status_code == 404
            assert exc_info.value.detail == "Shape card not found."