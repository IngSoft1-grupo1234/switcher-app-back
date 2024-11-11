import pytest
from unittest.mock import MagicMock, patch
from app.crud.match_crud import MatchRepository
from app.crud.movecard_crud import MoveCardRepository
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
def player_mock_session():
    with patch('app.crud.movecard_crud.session', autospec=True) as movecard_mock_session:
        yield movecard_mock_session


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
    password = ""

    match = match_repo.create_match(match_name, max_players, host, password)

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


pass_turn_return_board = [
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"]
]

pass_turn_return_shapes = {}

def test_pass_turn(match_repo, mock_session, player_mock_session):
    # esto es, creo, un conflict merge. Es abominable 
    mock_db = mock_session.return_value
    mock_match = MatchModel(match_id=1, match_name="Match1", max_players=4, host="1", player_count=2, current_turn=1, has_begun=True, players=[
        PlayerModel(player_id=1, username="Player1", match_id = 1, used_cards = json.dumps([]), shape_cards = []),
        PlayerModel(player_id=2, username="Player2", match_id = 1, used_cards = json.dumps([]), shape_cards = [])
    ],  turns=json.dumps([1, 2]), board = json.dumps(pass_turn_return_board), prohibited_color="")

    mock_player = PlayerModel(player_id=1, username="Player1", match_id = 1, used_cards = json.dumps([]), shape_cards = [])
    mock_db.query.return_value.get.return_value = mock_match
    mock_db.get.return_value = mock_match

    def mock_get(model, id):
        if model == PlayerModel and id == 1:
            return mock_player
        elif model == MatchModel and id == 1:
            return mock_match
        return None
    
    mock_db.query.side_effect = lambda model: MagicMock(get=lambda id: mock_get(model, id))

    with patch('app.crud.shapecard_crud.session', autospec=True) as shapecard_mock_session:
        shapecard_mock_db = shapecard_mock_session.return_value
        shapecard_mock_db.query.return_value.get.return_value = PlayerModel(player_id=1, username="Player1", match_id = 1, used_cards = json.dumps([]))
        with patch('app.crud.match_crud.MatchRepository.get_player_ids_in_match', return_value=[1, 2]),\
            patch('app.crud.shapecard_crud.ShapeCardRepository.get_amount_of_shape_cards_by_player', return_value=3),\
            patch('app.crud.movecard_crud.MoveCardRepository.get_amount_of_move_cards_by_player', return_value=3):
            player_mock_db = player_mock_session.return_value
            player_mock_db.get.return_value = PlayerModel(player_id=1, username="Player1", match_id = 1, used_cards = json.dumps([]))
            with patch('app.crud.movecard_crud.MoveCardRepository.confirm_moves', return_value=(pass_turn_return_board, pass_turn_return_shapes)): # borrar linea <<<
                result = match_repo.pass_turn(1, log=False, timercheck=False)

    assert result == (pass_turn_return_board, pass_turn_return_shapes)
    assert mock_match.current_turn == 2
    mock_db.commit.assert_called_once()



    





