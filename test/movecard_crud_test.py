import pytest
from unittest.mock import MagicMock, patch
from app.crud.movecard_crud import MoveCardRepository
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCardType
from fastapi import HTTPException


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

    move_card = move_card_repo.create_move_card(move_card_type)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert move_card.move_card_type == move_card_type


def test_create_move_card_type_not_exist(mock_session, move_card_repo):
    move_card_type = MoveCardType.MOV1
    mock_session_instance = mock_session.return_value

    mock_session_instance.query(MoveCardModel).filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.create_move_card(move_card_type)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Move card type does not exist"


def test_get_move_card_success(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.query.return_value.get.return_value = MoveCardModel(move_card_id=1, move_card_type=MoveCardType.MOV1)

    move_card = move_card_repo.get_move_card(1)

    assert move_card.move_card_id == 1
    assert move_card.move_card_type == MoveCardType.MOV1


def test_get_move_card_not_found(mock_session, move_card_repo):
    card_id = 1
    mock_session_instance = mock_session.return_value
    mock_session_instance.query(MoveCardModel).get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.get_move_card(card_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Move card not found"


def test_get_move_cards_by_player_success(mock_session, move_card_repo):
    mock_db = mock_session.return_value
    mock_db.query.return_value.filter.return_value.all.return_value = [
        MoveCardModel(move_card_id=1, player_id=1),
        MoveCardModel(move_card_id=2, player_id=1),
        MoveCardModel(move_card_id=3, player_id=1)
    ]

    move_cards = move_card_repo.get_move_cards_by_player(1)

    assert len(move_cards) == 3
    assert all(card.player_id == 1 for card in move_cards)


def test_get_move_cards_by_player_player_not_found(mock_session, move_card_repo):
    player_id = 1
    mock_session_instance = mock_session.return_value
    mock_session_instance.query(PlayerModel).get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.get_move_cards_by_player(player_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found"


def test_assign_move_card_to_player_successful_assignment(mock_session, move_card_repo):
    move_card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=move_card_id, is_active=False)
    
    move_card_repo.get_move_card = MagicMock(return_value=move_card)
    
    player = PlayerModel(player_id=player_id)
    mock_session_instance.query(PlayerModel).get.return_value = player
    
    result = move_card_repo.assign_move_card_to_player(move_card_id, player_id)
    
    assert result.move_card_id == move_card_id
    assert result.player_id == player_id
    assert result.is_active is True
    mock_session_instance.commit.assert_called_once()
    mock_session_instance.refresh.assert_called_once()


def test_assign_move_card_to_player_move_card_not_found(mock_session, move_card_repo):
    move_card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value
    mock_session_instance.query(MoveCardModel).get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Move card not found"


def test_assign_move_card_to_player_already_active_error(mock_session, move_card_repo):
    move_card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value
    move_card = MoveCardModel(move_card_id=move_card_id, is_active=True)
    mock_session_instance.query(MoveCardModel).get.return_value = move_card

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Move card is currently in use"


def test_assign_move_card_to_player_player_not_found_error(mock_session, move_card_repo):
    move_card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value
    move_card = MoveCardModel(move_card_id=move_card_id, is_active=False)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)
    mock_session_instance.query(PlayerModel).get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found"


def test_unassign_move_card_from_player_successful_unassignment(mock_session, move_card_repo):
    card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=card_id, is_active=True, player_id=player_id)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)

    player = PlayerModel(player_id=player_id)
    mock_session_instance.query(PlayerModel).get.return_value = player

    result = move_card_repo.unassign_move_card_from_player(card_id, player_id)

    assert result.move_card_id == card_id
    assert result.player_id is None
    assert result.is_active is False
    mock_session_instance.commit.assert_called_once()
    mock_session_instance.refresh.assert_called_once()


def test_unassign_move_card_from_player_card_not_found_error(mock_session, move_card_repo):
    card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card_repo.get_move_card = MagicMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.unassign_move_card_from_player(card_id, player_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Move card not found"


def test_unassign_move_card_from_player_not_active_error(mock_session, move_card_repo):
    card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=card_id, is_active=False)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.unassign_move_card_from_player(card_id, player_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Move card is not active and cannot be unassigned"


def test_unassign_move_card_from_player_player_not_found_error(mock_session, move_card_repo):
    card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=card_id, is_active=True)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)

    mock_session_instance.query(PlayerModel).get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.unassign_move_card_from_player(card_id, player_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found"
    

def test_unassign_move_card_from_player_not_owner_error(mock_session, move_card_repo):
    card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=card_id, is_active=True, player_id=2)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)

    player = PlayerModel(player_id=player_id)
    mock_session_instance.query(PlayerModel).get.return_value = player

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.unassign_move_card_from_player(card_id, player_id)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Player does not own this move card"


def test_assign_move_card_to_player_max_active_cards_error(mock_session, move_card_repo):
    move_card_id = 1
    player_id = 1
    mock_session_instance = mock_session.return_value

    move_card = MoveCardModel(move_card_id=move_card_id, is_active=False)
    move_card_repo.get_move_card = MagicMock(return_value=move_card)
    
    player = PlayerModel(player_id=player_id)
    mock_session_instance.query(PlayerModel).get.return_value = player
    
    mock_session_instance.query(MoveCardModel).filter.return_value.count.return_value = 3

    with pytest.raises(HTTPException) as exc_info:
        move_card_repo.assign_move_card_to_player(move_card_id, player_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Player already has 3 active move cards"