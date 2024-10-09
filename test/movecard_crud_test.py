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