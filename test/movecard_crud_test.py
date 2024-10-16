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
    