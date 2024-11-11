import pytest
from unittest.mock import MagicMock, patch
from app.crud.player_crud import PlayerRepository
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.shapecard_models import ShapeCard as ShapeCardModel 
from app.models.movecard_models import MoveCard as MoveCardModel
from app.crud.match_crud import MatchRepository
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import json

@pytest.fixture
def player_repo():
    return PlayerRepository()

@pytest.fixture
def mock_session():
    with patch('app.crud.player_crud.session') as mock_session:
        yield mock_session

@pytest.fixture
def move_mock_session():
    with patch('app.crud.movecard_crud.session') as move_mock_session:
        yield move_mock_session

def test_create_player(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.close = MagicMock()

    player = player_repo.create_player("test_user")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_db.close.assert_called_once()
    assert player.username == "test_user"

def test_get_player(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_player = PlayerModel(player_id=1, username="test_user")
    mock_db.get.return_value = mock_player
    mock_db.close = MagicMock()

    player = player_repo.get_player(1)

    mock_db.get.assert_called_once_with(PlayerModel, 1)
    mock_db.close.assert_called_once()
    assert player.username == "test_user"
    assert player.player_id == 1

def test_assign_match_to_player(mock_session, player_repo):
    match = MatchModel(match_id=1, player_count=3, password="", players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2), 
                                                PlayerModel(player_id=3)])
    with patch.object(MatchRepository, 'get_match', return_value=match):
        mock_db = mock_session.return_value
        mock_db.get.side_effect = [PlayerModel(player_id=4), match]
        mock_db.commit = MagicMock()
        mock_db.close = MagicMock()

        result = player_repo.assign_match_to_player(4, 1, log=False)

        mock_db.get.assert_any_call(PlayerModel, 4)
        mock_db.commit.assert_called_once()
        assert result is None

def test_assign_match_to_player_match_not_found(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_db.get.side_effect = [PlayerModel(player_id=1), None]
    mock_db.close = MagicMock()
    with patch.object(MatchRepository, 'get_match', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            player_repo.assign_match_to_player(1, 1)

    mock_db.get.assert_any_call(PlayerModel, 1)
    assert exc_info.value.detail == "Match not found."

def test_assign_match_to_player_player_not_found(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_db.get.side_effect = [None, MatchModel(match_id=1)]
    mock_db.close = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        player_repo.assign_match_to_player(1, 1)

    mock_db.get.assert_any_call(PlayerModel, 1)
    assert exc_info.value.detail == "Player not found."

def test_assign_match_to_player_integrity_error(mock_session, player_repo):
    match = MatchModel(match_id=1, player_count=4, password="",players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2), 
                                                PlayerModel(player_id=3), 
                                                PlayerModel(player_id=4)])
    mock_db = mock_session.return_value
    mock_db.get.side_effect = [PlayerModel(player_id=5), match]
    mock_db.commit.side_effect = IntegrityError("mock", "mock", "mock")
    mock_db.close = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        player_repo.assign_match_to_player(1, 1, log=False)

    mock_db.get.assert_any_call(PlayerModel, 1)
    assert exc_info.value.detail == "Match is full."

def test_assign_match_to_player_password(mock_session, player_repo):
    match = MatchModel(match_id=1, player_count=3, password="contraseña123", players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2)])
    with patch.object(MatchRepository, 'get_match', return_value=match):
        mock_db = mock_session.return_value
        mock_db.get.side_effect = [PlayerModel(player_id=3), match]
        mock_db.commit = MagicMock()
        mock_db.close = MagicMock()

        result = player_repo.assign_match_to_player(3, 1, "contraseña123", log=False)

        mock_db.get.assert_any_call(PlayerModel, 3)
        mock_db.commit.assert_called_once()
        assert result is None


        

def test_assign_match_to_player_bad_password(mock_session, player_repo):
    match = MatchModel(match_id=1, player_count=3, password="contraseña123", players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2)])
    with patch.object(MatchRepository, 'get_match', return_value=match):
        mock_db = mock_session.return_value
        mock_db.get.side_effect = [PlayerModel(player_id=3), match]
        mock_db.commit = MagicMock()
        mock_db.close = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            player_repo.assign_match_to_player(3, 1, "", log=False)
            assert exc_info.value.detail == "Incorrect password."

        mock_db.get.assert_any_call(PlayerModel, 3)
    
        
def test_unassign_match_to_player(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_db.get.side_effect = [
        PlayerModel(player_id=1, match_id=1),
        MatchModel(player_count=1, has_begun=False, host=2, players=[])
    ]
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()
    with patch('app.crud.match_crud.session', return_value=mock_db):
        result = player_repo.unassign_match_to_player(1, log=False)
        
        mock_db.get.assert_any_call(PlayerModel, 1)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()
        assert result is None

def test_delete_player(mock_session, player_repo):
    mock_db = mock_session.return_value

    mock_player = PlayerModel(player_id=1)
    mock_match = MatchModel(player_count=1)
    mock_player.match = mock_match

    mock_db.get.return_value = mock_player

    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    player_repo.delete_player(1)

    mock_db.get.assert_called_once_with(PlayerModel, 1)

    mock_db.commit.assert_called_once()


board = json.dumps([
    ["r", "g", "b", "y", "r", "g"],
    ["r", "r", "y", "r", "g", "b"],
    ["r", "y", "r", "b", "b", "y"],
    ["y", "r", "g", "g", "y", "r"],
    ["r", "g", "g", "y", "r", "g"],
    ["g", "b", "y", "r", "g", "b"]
])

pass_turn_return_board = [
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"],
    ["r", "r", "r", "r", "r", "r"]
]

pass_turn_return_shapes = {}

def test_use_shape_card(mock_session, player_repo):
    mock_db = mock_session.return_value
    match = MatchModel(match_id=1, turns=json.dumps([1, 2, 3]), current_turn=1, board=board, prohibited_color="")
    mock_db.get.side_effect = [
        ShapeCardModel(shape_card_id=1, player_id=1, is_active=True),  # Para ShapeCardModel
        PlayerModel(player_id=1, match_id=1, matches=match),  # Para PlayerModel
        match  # Para MatchModel
    ]

    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    with patch('app.crud.shapecard_crud.ShapeCardRepository.get_shape_card') as mock_shape_card,\
         patch('app.crud.shapecard_crud.ShapeCardRepository.set_active_shape_card'),\
         patch('app.crud.movecard_crud.MoveCardRepository.get_amount_of_move_cards_by_player', return_value=3),\
         patch('app.crud.movecard_crud.MoveCardRepository.confirm_moves', return_value=(pass_turn_return_board, pass_turn_return_shapes)): 
            mock_shape_card.return_value = MagicMock()
            player_repo.use_shape_card(1, "r", "(1,0)", log=False)

    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()


def test_winner_without_shape_card(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_player = PlayerModel(player_id=1, username="test_user", match_id=1)
    mock_other_player = PlayerModel(player_id=2, username="other_user", match_id=1)
    mock_player.shape_cards = []  
    mock_other_player.shape_cards = [ShapeCardModel(shape_card_id=1)]
    
    mock_match = MatchModel(match_id=1, has_begun=True, host=1, players=[mock_player, mock_other_player], player_count=2)
    mock_player.matches = mock_match
    
    mock_moves = [MoveCardModel(move_card_id=1, match_id=1, player_id=1),
                  MoveCardModel(move_card_id=2, match_id=1, player_id=2)]
    
    def mock_get(model, id):
        if model == PlayerModel and id == 1:
            return mock_player
        elif model == PlayerModel and id == 2:
            return mock_other_player
        elif model == MatchModel and id == 1:
            return mock_match
        elif model == MoveCardModel and id in [1, 2]:
            return next((move for move in mock_moves if move.move_card_id == id), None)
        return None

    def mock_query(model):
        query_mock = MagicMock()
        if model == MoveCardModel:
            query_mock.filter.return_value.all.return_value = mock_moves
        elif model == ShapeCardModel:
            if mock_db.get(PlayerModel, 2):  
                query_mock.filter.return_value.all.return_value = mock_other_player.shape_cards
            else:
                query_mock.filter.return_value.all.return_value = []
        return query_mock

    mock_db.get.side_effect = mock_get
    mock_db.query.side_effect = mock_query
    mock_db.delete = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()
    
    
    result = player_repo.winner_without_shape_card(1, log=False)

    mock_db.get.assert_any_call(PlayerModel, 1)
    mock_db.get.assert_any_call(MatchModel, 1)
    
    assert mock_db.delete.call_count == 5 
    mock_db.commit.assert_called_once()  
    mock_db.close.assert_called_once() 

    assert result == {"winner_username": "test_user", "winner_player_id": 1}

@pytest.mark.asyncio
async def test_player_message(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_player = PlayerModel(player_id=1, username="test_user", match_id=1)
    mock_match = MatchModel(match_id=1, has_begun=True, host=1, players=[mock_player], player_count=1, chats=[])

    def mock_get(model, id):
        if model == PlayerModel and id == 1:
            return mock_player
        elif model == MatchModel and id == 1:
            return mock_match
        return None
    
    mock_db.get.side_effect = mock_get
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()
    
    player_repo.player_send_message(1, "Me encanta el testing, me encanta estar 5 horas arreglando una linea de codigo.")

    mock_db.get.assert_any_call(PlayerModel, 1)
    mock_db.get.assert_any_call(MatchModel, 1)


















