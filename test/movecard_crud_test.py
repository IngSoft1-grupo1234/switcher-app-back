import pytest
from unittest.mock import MagicMock, patch
from app.crud.movecard_crud import MoveCardRepository
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCardType
from app.schemas.movecard_schemas import MoveCardIn
from fastapi import HTTPException
import json
import random

@pytest.fixture
def mock_session():
    with patch('app.crud.movecard_crud.session') as mock_session:
        yield mock_session


@pytest.fixture
def move_card_repo():
    return MoveCardRepository()


def test_create_move_card_success(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    move_card_type = MoveCardType.MOV1
    match_id = 1

    move_card_repo.create_move_card(match_id, move_card_type)


    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_create_move_card_invalid_type(mock_session, move_card_repo):
    match_id = 1
    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.create_move_card(match_id, "INVALID_TYPE")
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Move card type does not exist"


def test_create_move_card_limit_exceeded(mock_session, move_card_repo):
    match_id = 1
    mock_session.return_value.query.return_value.filter.return_value.first.return_value = MoveCardModel(move_card_type=MoveCardType.MOV1)

    mock_session.return_value.query.return_value.filter.return_value.count.return_value = 7

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.create_move_card(match_id, MoveCardType.MOV1)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Cannot create more than 7 move cards of the same type"


def test_get_move_cards_id_in_match_no_move_cards_found(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    match_id = 1

    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.get_move_cards_id_in_match(match_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "No move cards found for this match"


def test_assign_move_card_to_player_success(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    player_id = 1
    match_id = 1
    move_card_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id
    mock_player.move_cards = []
    mock_player.match_id = match_id

    mock_move_card = MagicMock()
    mock_move_card.move_card_id = move_card_id
    mock_move_card.player_id = None
    mock_move_card.is_active = False
    mock_move_card.match_id = match_id

    mock_match = MagicMock()
    mock_match.match_id = match_id


    mock_db.get.side_effect = [
        mock_player,
        mock_move_card,
        mock_match
    ]

    move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    mock_db.commit.assert_called_once()
    assert mock_move_card.player_id == player_id
    assert mock_move_card.is_active is True
    assert mock_player.move_cards == [mock_move_card]


def test_assign_move_card_to_player_move_card_not_found(mock_session, move_card_repo):
    player_id = 1
    move_card_id = 1

    mock_session.return_value.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)
    
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Move card not found"


def test_assign_move_card_to_player_move_card_already_active(mock_session, move_card_repo):
    player_id = 1
    move_card_id = 1

    mock_move_card = MagicMock()
    mock_move_card.is_active = True

    mock_session.return_value.get.return_value = mock_move_card

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Move card is currently in use"


def test_assign_move_card_to_player_move_card_already_assigned(mock_session, move_card_repo):
    player_id = 1
    move_card_id = 1

    mock_move_card = MagicMock()
    mock_move_card.is_active = False
    mock_move_card.player_id = 2

    mock_session.return_value.get.return_value = mock_move_card

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Move card is already assigned to a player"


def test_assign_move_card_to_player_player_not_found(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1
    move_card_id = 1

    mock_player = None

    mock_move_card = MagicMock()
    mock_move_card.move_card_id = move_card_id
    mock_move_card.player_id = None
    mock_move_card.is_active = False

    mock_db.get.side_effect = [
        mock_player,
        mock_move_card
    ]

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Player not found"


def test_assign_move_card_to_player_player_move_card_limit_exceeded(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1
    move_card_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id
    mock_player.match_id = 1
    mock_player.move_cards = [MagicMock() for _ in range(3)]

    mock_move_card = MagicMock()
    mock_move_card.move_card_id = move_card_id
    mock_move_card.player_id = None
    mock_move_card.is_active = False
    mock_move_card.match_id = 1

    mock_db.get.side_effect = [
        mock_player,
        mock_move_card
    ]

    mock_db.query.return_value.filter.return_value.count.return_value = 3

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Player already has 3 active move cards"
    

def test_assign_move_card_to_player_move_card_not_in_match(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1
    move_card_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id
    mock_player.match_id = 1

    mock_move_card = MagicMock()
    mock_move_card.move_card_id = move_card_id
    mock_move_card.player_id = None
    mock_move_card.is_active = False
    mock_move_card.match_id = 2

    mock_db.get.side_effect = [
        mock_player,
        mock_move_card
    ]

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Move card does not belong to the player's match"


def test_get_move_cards_by_player_success(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id

    mock_move_cards = [MagicMock() for _ in range(3)]

    mock_db.get.return_value = mock_player
    mock_db.query.return_value.filter.return_value.all.return_value = mock_move_cards

    result = move_card_repo.get_move_cards_by_player(player_id)

    assert result == mock_move_cards


def test_get_move_cards_by_player_player_not_found(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_db.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.get_move_cards_by_player(player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Player not found"


def test_get_move_cards_by_player_no_move_cards_found(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id

    mock_db.get.return_value = mock_player
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(HTTPException) as excinfo:
        move_card_repo.get_move_cards_by_player(player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "No move cards found for this player"

def test_confirm_move(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    # Create mock objects for PlayerModel, MatchModel, and MoveCardModel
    mock_player = MagicMock()
    mock_player.match_id = 1
    mock_player.player_id = 1
    mock_player.used_cards = json.dumps([1, 2, 3])

    mock_match = MagicMock()
    board = [[random.choice(['r', 'g', 'b', 'y']) for _ in range(6)] for _ in range(6)]
    mock_match.board = json.dumps(board)
    

    mock_move_card = MagicMock()
    mock_move_card.move_card_type.value = 1
    mock_move_card.last_used_orientation = 'right'
    mock_move_card.last_used_position = json.dumps([2, 2])
    
    # Configure the mock session to return the mock objects
    def mock_get(model, id):
            if model == PlayerModel:
                return mock_player
            elif model == MatchModel:
                return mock_match
            elif model == MoveCardModel:
                return mock_move_card
            return None

    mock_db.get.side_effect = mock_get

    
    move_card_repo.confirm_moves(player_id=1)

    mock_db.get.assert_any_call(PlayerModel, 1)
    mock_db.get.assert_any_call(MatchModel, 1)
    mock_db.get.assert_any_call(MoveCardModel, 1)

def test_soft_move(mock_session, move_card_repo):
    mock_db = mock_session.return_value

    mock_player = MagicMock()
    mock_player.match_id = 1
    mock_player.player_id = 1
    mock_player.used_cards = json.dumps([])
    mock_player.matches = MagicMock()
    mock_player.matches.current_turn = 1

    mock_match = MagicMock()
    board = [[random.choice(['r', 'g', 'b', 'y']) for _ in range(6)] for _ in range(6)]
    mock_match.board = json.dumps(board)
    mock_match.current_turn = 1
    

    card = MoveCardModel(move_card_id=1, 
                         move_card_type= MoveCardType.MOV1, 
                         player_id=1, 
                         match_id=1, 
                         is_active=True, 
                         last_used_orientation="right", 
                         last_used_position=json.dumps([2, 2]))
    mock_move_card = card

    def mock_get(model, id):
            if model == PlayerModel:
                return mock_player
            elif model == MatchModel:
                return mock_match
            elif model == MoveCardModel:
                return mock_move_card
            return None

    mock_db.get.side_effect = mock_get

    movement_info = MoveCardIn(orientation="right", position=json.dumps([0, 0]))
    bad_movement_info = MoveCardIn(orientation="up", position=json.dumps([0, 0]))

    with patch.object(move_card_repo, "get_move_cards_by_player", return_value=[card]):
        # valido
        
        move_card_repo.soft_move(player_id=1, move_card_id=1, movement_info=movement_info, log=False)
        
        error_cases = [
            (1, 1, movement_info, 400, "Move card already used"),
            (1, 1, bad_movement_info, 400, "Invalid move"),
            (1, 2, movement_info, 404, "Move card not found"),
            (2, 1, movement_info, 404, "Player not found"),
        ]

        for player_id, move_card_id, movement_info, status_code, detail in error_cases:
            with pytest.raises(HTTPException) as excinfo:
                move_card_repo.soft_move(player_id=player_id, move_card_id=move_card_id, movement_info=movement_info, log=False)
                assert excinfo.value.status_code == status_code
                assert excinfo.value.detail == detail

        with pytest.raises(HTTPException) as excinfo:
            mock_player.matches.current_turn = 2
            mock_match.current_turn = 2
            move_card_repo.soft_move(player_id=1, move_card_id=1, movement_info=movement_info, log=False)
            assert excinfo.value.status_code == 400
            assert excinfo.value.detail == "Not player's turn"

def test_cancel_soft_move(mock_session, move_card_repo):
        # Create a mock session
        mock_db = mock_session.return_value

        # Create a mock move card
        mock_move_card = MoveCardModel(move_card_id=1, 
                         move_card_type= MoveCardType.MOV1, 
                         player_id=1, 
                         match_id=1, 
                         is_active=True, 
                         last_used_orientation="right", 
                         last_used_position=json.dumps([2, 2]))

        # player and match
        board = [[random.choice(['r', 'g', 'b', 'y']) for _ in range(6)] for _ in range(6)]
        mock_player = PlayerModel(player_id=1, 
                                  match_id=1, 
                                  used_cards=json.dumps([1]),
                                  matches=MatchModel(current_turn=1, board=json.dumps(board)),
                                  move_cards = [mock_move_card]
                                  )
        
        

        # Configure the mock session to return the mock move card
        def mock_get(model, id):
            if model == MoveCardModel and id == 1:
                return mock_move_card
            elif model == PlayerModel and id == 1:
                return mock_player
            return None

        mock_db.get.side_effect = mock_get
        
        # Call the function with a valid move card
        move_card_repo.cancel_soft_move(player_id=1, log=False)


def test_get_amount_of_move_cards_by_player(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.get.return_value = PlayerModel(player_id=1)
    mock_db.query.return_value.filter.return_value.count.return_value = 5
    mock_db.close = MagicMock()

    move_card_count = move_card_repo.get_amount_of_move_cards_by_player(1)

    mock_db.get.assert_called_once_with(PlayerModel, 1)
    mock_db.query.assert_called_once()
    mock_db.close.assert_called_once()
    assert move_card_count == 5

def test_get_amount_of_move_cards_by_player_player_not_found(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.get.return_value = None
    mock_db.close = MagicMock()

    try:
        move_card_repo.get_amount_of_move_cards_by_player(999)
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Player not found"

    mock_db.get.assert_called_once_with(PlayerModel, 999)
    mock_db.close.assert_called_once()
