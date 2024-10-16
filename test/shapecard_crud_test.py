import pytest
from unittest.mock import MagicMock, patch
from app.crud.shapecard_crud import ShapeCardRepository
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from fastapi import HTTPException


@pytest.fixture
def mock_session():
    with patch('app.crud.shapecard_crud.session') as mock_session:
        yield mock_session


@pytest.fixture
def shape_card_repo():
    return ShapeCardRepository()


def test_create_shape_card_success(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    shape_card_type = ShapeCardType.SHAPE1

    shape_card_repo.create_shape_card(shape_card_type)


    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_create_shape_card_invalid_type(mock_session, shape_card_repo):
    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.create_shape_card("INVALID_TYPE")
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Shape card type does not exist"


def test_assign_shape_card_to_player_success(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    player_id = 1
    shape_card_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id
    mock_player.shape_cards = []
  
    mock_shape_card = MagicMock()
    mock_shape_card.shape_card_id = shape_card_id
    mock_shape_card.player_id = None
    mock_shape_card.is_active = False

    mock_db.get.side_effect = [
        mock_player,
        mock_shape_card
    ]

    shape_card_repo.assign_shape_card_to_player(shape_card_id, player_id)

    mock_db.commit.assert_called_once()
    assert mock_shape_card.player_id == player_id
    assert mock_player.shape_cards == [mock_shape_card]


def test_assign_shape_card_to_player_shape_card_not_found(mock_session, shape_card_repo):
    player_id = 1
    shape_card_id = 1

    mock_session.return_value.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.assign_shape_card_to_player(shape_card_id, player_id)
    
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Shape card not found"


def test_assign_shape_card_to_player_shape_card_already_assigned(mock_session, shape_card_repo):
    player_id = 1
    shape_card_id = 1

    mock_shape_card = MagicMock()
    mock_shape_card.is_active = False
    mock_shape_card.player_id = 2

    mock_session.return_value.get.return_value = mock_shape_card

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.assign_shape_card_to_player(shape_card_id, player_id)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Shape card is already assigned to a player"


def test_assign_shape_card_to_player_player_not_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    player_id = 1
    shape_card_id = 1

    mock_player = None

    mock_shape_card = MagicMock()
    mock_shape_card.shape_card_id = shape_card_id
    mock_shape_card.player_id = None
    mock_shape_card.is_active = False

    mock_db.get.side_effect = [
        mock_player,
        mock_shape_card
    ]

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.assign_shape_card_to_player(shape_card_id, player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Player not found"


def test_set_active_shape_card_success(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_db.commit = MagicMock()

    shape_card_id = 1

    mock_shape_card = MagicMock()
    mock_shape_card.shape_card_id = shape_card_id
    mock_shape_card.player_id = 1
    mock_shape_card.is_active = False

    mock_db.get.return_value = mock_shape_card

    shape_card_repo.set_active_shape_card(shape_card_id)

    mock_db.commit.assert_called_once()
    assert mock_shape_card.is_active == True


def test_set_active_shape_card_shape_card_not_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    shape_card_id = 1

    mock_db.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.set_active_shape_card(shape_card_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Shape card not found"


def test_set_active_shape_card_shape_card_not_assigned_to_player(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    shape_card_id = 1

    mock_shape_card = MagicMock()
    mock_shape_card.shape_card_id = shape_card_id
    mock_shape_card.player_id = None

    mock_db.get.return_value = mock_shape_card

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.set_active_shape_card(shape_card_id)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Shape card is not assigned to a player"
    

def test_set_active_shape_card_shape_card_already_active(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    shape_card_id = 1

    mock_shape_card = MagicMock()
    mock_shape_card.shape_card_id = shape_card_id
    mock_shape_card.player_id = 1
    mock_shape_card.is_active = True

    mock_db.get.return_value = mock_shape_card

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.set_active_shape_card(shape_card_id)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Shape card is already active"


def test_get_shape_cards_by_player_success(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id

    mock_shape_cards = [MagicMock() for _ in range(3)]

    mock_db.get.return_value = mock_player
    mock_db.query.return_value.filter.return_value.all.return_value = mock_shape_cards

    result = shape_card_repo.get_shape_cards_by_player(player_id)

    assert result == mock_shape_cards


def test_get_shape_cards_by_player_player_not_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_db.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.get_shape_cards_by_player(player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Player not found"


def test_get_shape_cards_by_player_no_shape_cards_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value

    player_id = 1

    mock_player = MagicMock()
    mock_player.player_id = player_id

    mock_db.get.return_value = mock_player
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(HTTPException) as excinfo:
        shape_card_repo.get_shape_cards_by_player(player_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "No shape cards actives found for this player"

def test_get_shape_card(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_shape_card = ShapeCardModel(shape_card_id=1, shape_card_type=ShapeCardType.SHAPE1)
    mock_db.get.return_value = mock_shape_card
    mock_db.close = MagicMock()

    shape_card = shape_card_repo.get_shape_card(1)

    mock_db.get.assert_called_once_with(ShapeCardModel, 1)
    mock_db.close.assert_called_once()
    assert shape_card.shape_card_type == ShapeCardType.SHAPE1
    assert shape_card.shape_card_id == 1


def test_get_shape_card_not_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_db.get.return_value = None
    mock_db.close = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        shape_card_repo.get_shape_card(1)

    mock_db.get.assert_called_once_with(ShapeCardModel, 1)
    mock_db.close.assert_called_once()
    assert exc_info.value.detail == "Shape card not found"


def test_get_shape_cards_ids_inactive(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    mock_db.query.return_value.filter.return_value.all.return_value = [(1,), (2,)]
    mock_db.close = MagicMock()

    shape_card_ids = shape_card_repo.get_shape_cards_ids_inactive(1)

    mock_db.query.assert_called_once()
    mock_db.close.assert_called_once()
    assert shape_card_ids == [1, 2]

def test_get_amount_of_shape_cards_by_player(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    
    mock_db.get.return_value = PlayerModel(player_id=1)

    mock_db.query.return_value.filter.return_value.count.return_value = 3

    mock_db.close = MagicMock()

    shape_card_count = shape_card_repo.get_amount_of_shape_cards_by_player(1)

    mock_db.get.assert_called_once_with(PlayerModel, 1)
    mock_db.query.assert_called_once()
    mock_db.close.assert_called_once()
    assert shape_card_count == 3 

def test_get_amount_of_shape_cards_by_player_player_not_found(mock_session, shape_card_repo):
    mock_db = mock_session.return_value
    
    mock_db.get.return_value = None

    mock_db.close = MagicMock()

    try:
        shape_card_repo.get_amount_of_shape_cards_by_player(999)
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Player not found"

    mock_db.get.assert_called_once_with(PlayerModel, 999)
    mock_db.close.assert_called_once()

    