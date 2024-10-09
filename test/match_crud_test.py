import pytest
from unittest.mock import MagicMock, patch
from app.crud.match_crud import MatchRepository
from app.models.match_models import Match as MatchModel
from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.crud.movecard_crud import MoveCardRepository

import json

@pytest.fixture
def mock_session():
    with patch('app.crud.match_crud.session', autospec=True) as mock_session:
        yield mock_session

@pytest.fixture
def match_repo(mock_session):
    return MatchRepository()

def test_create_match(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    match_name = "Test Match"
    max_players = 4
    host = "Host1"

    match = match_repo.create_match(match_name, max_players, host)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert match.match_name == match_name
    assert match.max_players == max_players
    assert match.host == host

def test_get_all_matches(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_db.query.return_value.all.return_value = [
        MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=False, players=[
            PlayerModel(player_id=1, username="Player1"),
            PlayerModel(player_id=2, username="Player2")
        ])
    ]

    result = match_repo.get_all_matches()

    assert len(result["matches"]) == 1
    assert result["matches"][0]["match_name"] == "Match1"

def test_get_notbegun_matches(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_db.query.return_value.filter.return_value.all.return_value = [
        MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=False, players=[
            PlayerModel(player_id=1, username="Player1"),
            PlayerModel(player_id=2, username="Player2")
        ])
    ]

    result = match_repo.get_notbegun_matches()

    assert len(result["matches"]) == 1
    assert result["matches"][0]["match_name"] == "Match1"

def test_get_match(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_db.query.return_value.get.return_value = MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=False, players=[
        PlayerModel(player_id=1, username="Player1"),
        PlayerModel(player_id=2, username="Player2")
    ])

    result = match_repo.get_match_dict(1)

    assert result["match_name"] == "Match1"

def test_delete_match(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_match = MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=False, players=[
        PlayerModel(player_id=1, username="Player1"),
        PlayerModel(player_id=2, username="Player2")
    ])
    mock_db.query.return_value.get.return_value = mock_match

    result = match_repo.delete_match(1)

    assert result == None
    mock_db.delete.assert_called_once_with(mock_match)
    mock_db.commit.assert_called_once()

def test_start_match(mock_session, match_repo):
    mock_db = mock_session.return_value
    mock_match = MatchModel(
        match_id=1, 
        match_name="Match1", 
        max_players=4, 
        host="Host1", 
        player_count=2, 
        current_turn=1, 
        has_begun=False, 
        players=[
            PlayerModel(player_id=1, username="Player1"),
            PlayerModel(player_id=2, username="Player2")
        ],
        move_cards=[]
    )
    mock_db.query.return_value.get.return_value = mock_match

    # Mockear MoveCardRepository para evitar crear cartas de movimiento reales
    mock_move_card = MagicMock()
    mock_move_card.move_card_id = 1
    mock_move_card.player_id = None
    mock_move_card.is_active = False
    mock_move_card.match_id = 1
    mock_move_card.move_card_type = MoveCardType.MOV1

    with patch('app.crud.movecard_crud.MoveCardRepository.create_move_card', return_value=mock_move_card) as mock_create_move_card, \
            patch('app.crud.movecard_crud.MoveCardRepository.assign_move_card_to_player') as mock_assign_move_card_to_player:
            
    

        result = match_repo.start_match(1)

    assert result == [1, 2] or result == [2, 1] # abominacion pero es viable con dos jugadores
    assert mock_match.has_begun is True
    mock_db.commit.assert_called_once()


def test_set_player_count(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_match = MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=False, players=[
        PlayerModel(player_id=1, username="Player1"),
        PlayerModel(player_id=2, username="Player2")
    ])
    mock_db.query.return_value.get.return_value = mock_match

    result = match_repo.set_player_count(1, 3)

    assert result == None
    assert mock_match.player_count == 3
    mock_db.commit.assert_called_once()



def test_pass_turn(match_repo, mock_session):
    mock_db = mock_session.return_value
    mock_match = MatchModel(match_id=1, match_name="Match1", max_players=4, host="Host1", player_count=2, current_turn=1, has_begun=True, players=[
        PlayerModel(player_id=1, username="Player1"),
        PlayerModel(player_id=2, username="Player2")
    ],  turns=json.dumps([1, 2]))
    mock_db.query.return_value.get.return_value = mock_match

    result = match_repo.pass_turn(1)

    assert result == None
    assert mock_match.current_turn == 2
    mock_db.commit.assert_called_once()



    





