import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.routers.match_routers import router
from app.crud.match_crud import MatchRepository
from app.crud.player_crud import PlayerRepository
from app.crud.movecard_crud import MoveCardRepository
from app.crud.shapecard_crud import ShapeCardRepository



client = TestClient(router)

def test_create_match():
    expected_response = {
        "match_name": "test_match",
        "max_players": 4,
        "host": 1,
        "match_id": 1,
        "operation_result": "Succesfully created!"
     }
    
    with patch.object(MatchRepository, 'create_match', return_value=MagicMock(**expected_response)),\
            patch.object(PlayerRepository, 'get_player', return_value=MagicMock()),\
            patch.object(PlayerRepository, 'assign_match_to_player', return_value=None):
            response = client.post("/matches/", json={"match_name": "test_match",
                                                    "max_players": 4,
                                                    "host": 1})
            
            assert response.status_code == 201
            assert response.json() == expected_response

def test_get_match():
    expected_response = {
        "id": 1,
        "match_name": "test_match",
        "max_players": 4,
        "host": 1,
        "player_count": 1,
        "current_turn": 1,
        "has_begun": False,
        "players": []
    }
    with patch.object(MatchRepository, 'get_match_dict', return_value=expected_response):
        response = client.get(f"/matches/1")
        assert response.status_code == 200
        assert response.json() == expected_response

def test_get_all_match():
    expected_response = { "matches" : [{
        "id": 1,
        "match_name": "test_match_1",
        "max_players": 4,
        "host": 1,
        "player_count": 1,
        "current_turn": 1,
        "has_begun": False,
        "players": []
    },
    {
        "id": 2,
        "match_name": "test_match_2",
        "max_players": 4,
        "host": 5,
        "player_count": 1,
        "current_turn": 1,
        "has_begun": True,
        "players": []
    },]
    }

    with patch.object(MatchRepository, 'get_all_matches', return_value=expected_response):
        response = client.get(f"/matches/")
        assert response.status_code == 200
        assert response.json() == expected_response

def test_get_notbegun_matches():
    expected_response = { "matches" : [{
        "id": 1,
        "match_name": "test_match_1",
        "max_players": 4,
        "host": 1,
        "player_count": 1,
        "current_turn": 1,
        "has_begun": False,
        "players": []
    }]
    }
    with patch.object(MatchRepository, 'get_notbegun_matches', return_value=expected_response):
        response = client.get(f"/matches/notbegun/")
        assert response.status_code == 200
        assert response.json() == expected_response

    
start_match_return_value = {
    "turns" : [1, 2],
    "board" : [["r", "r", "r", "r", "r", "r"],
               ["r", "r", "r", "r", "r", "r"],
               ["r", "r", "r", "r", "r", "r"],
               ["r", "r", "r", "r", "r", "r"],
               ["r", "r", "r", "r", "r", "r"],
               ["r", "r", "r", "r", "r", "r"]],
    "shapes" : {}
}
def test_start_match():
    match_id = 1
    move_card1_type = MagicMock(value='1')
    move_card2_type = MagicMock(value='2')
    move_card1 = MagicMock(move_card_type=move_card1_type)
    move_card2 = MagicMock(move_card_type=move_card2_type)
    shape_card1_type = MagicMock(value='1')
    shape_card2_type = MagicMock(value='2')
    shape_card1 = MagicMock(shape_card_type=shape_card1_type)
    shape_card2 = MagicMock(shape_card_type=shape_card2_type)
    with patch.object(MatchRepository, 'start_match', return_value=start_match_return_value),\
            patch.object(MoveCardRepository, 'get_move_cards_by_player', return_value=[move_card1, move_card2]),\
            patch.object(ShapeCardRepository, 'get_shape_cards_by_player', return_value=[shape_card1, shape_card2]):
        response = client.put(f"/matches/{match_id}/start")
        assert response.status_code == 204

def test_start_match_not_found():
    with patch('app.crud.match_crud.session') as mock_session:
        mock_query = mock_session.return_value.query.return_value
        mock_query.get.return_value = None  

        with pytest.raises(HTTPException) as exc_info:
            client.put("/matches/999/start")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Match not found."


b = [
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"]
]

s = {}

def test_pass_turn():
    expected_response = {
        "username": "Player2",
        "player_id": 2
    }
    with patch.object(MatchRepository, 'get_next_player', return_value=expected_response),\
            patch.object(MatchRepository, 'pass_turn', return_value=(b,s)),\
            patch.object(MatchRepository, 'get_player_ids_in_match', return_value=[1, 2]):
        response = client.put("/matches/1/next_turn")
        assert response.status_code == 204



def test_pass_turn_match_not_found():
    with patch('app.crud.match_crud.MatchRepository.pass_turn', return_value=(b,s)):
        with patch('app.crud.match_crud.MatchRepository.get_next_player', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                client.put("/matches/999/next_turn")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Match not found."


def test_pass_turn_no_next_player():
    with patch('app.crud.match_crud.MatchRepository.pass_turn', return_value=(b,s)):
        with patch('app.crud.match_crud.MatchRepository.get_next_player', return_value=None),\
            patch('app.crud.match_crud.MatchRepository.get_player_ids_in_match', return_value=[1, 2]):
                with pytest.raises(HTTPException) as exc_info:
                    response = client.put("/matches/1/next_turn")
                    assert response.status_code == 404  








