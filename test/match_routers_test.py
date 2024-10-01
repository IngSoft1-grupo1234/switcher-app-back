import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.routers.match_routers import router
from app.crud.match_crud import MatchRepository



client = TestClient(router)

""" def test_create_match():
    expected_response = {
        "match_name": "test_match",
        "max_players": 4,
        "host": 1,
        "match_id": 1,
        "operation_result": "Succesfully created!"
    }
    with patch.object(MatchRepository, 'create_match', return_value=expected_response):
        response = client.post("/matches/", json={"match_name": "test_match",
                                                  "max_players": 4,
                                                  "host": 1})
        assert response.status_code == 201
        assert response.json() == expected_response """

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
    with patch.object(MatchRepository, 'get_match', return_value=expected_response):
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

def test_delete_match():
    with patch.object(MatchRepository, 'delete_match', return_value=True):
        response = client.delete(f"/matches/1")
        assert response.status_code == 204
    
def test_start_match():
    match_id = 1
    with patch.object(MatchRepository, 'start_match', return_value="started"):
        response = client.put(f"/matches/{match_id}/start")
        assert response.status_code == 204

def test_set_match_turn():
    with patch.object(MatchRepository, 'set_match_turn', return_value="success"):
        response = client.put(f"/matches/1/turn/1")
        assert response.status_code == 204

def test_set_player_count():
    with patch.object(MatchRepository, 'set_player_count', return_value="success"):
        response = client.put(f"/matches/1/player_count/1")
        assert response.status_code == 204
    
def test_match_not_found():
    match_id = 999
    with patch.object(MatchRepository, 'delete_match', return_value=False): # delete match
        with pytest.raises(HTTPException) as exc_info:
            response = client.delete(f"/matches/{match_id}")
            assert response.status_code == 404
            assert exc_info.value.detail == "Match not found."
    with patch.object(MatchRepository, 'start_match', return_value=False): # start match
        with pytest.raises(HTTPException) as exc_info:
            response = client.put(f"/matches/{match_id}/start")
            assert response.status_code == 404
            assert exc_info.value.detail == "Match not found."
    with patch.object(MatchRepository, 'set_player_count', return_value=False): # set player count
        with pytest.raises(HTTPException) as exc_info:
            response = client.put(f"/matches/1/player_count/1")
            assert response.status_code == 404
            assert exc_info.value.detail == "Match not found."
    