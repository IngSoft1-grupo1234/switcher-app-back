import pytest
from unittest.mock import MagicMock, patch
from app.crud.player_crud import PlayerRepository
from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.crud.match_crud import MatchRepository
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


@pytest.fixture
def player_repo():
    return PlayerRepository()

@pytest.fixture
def mock_session():
    with patch('app.crud.player_crud.session') as mock_session:
        yield mock_session

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
    match = MatchModel(match_id=1, player_count=3, players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2), 
                                                PlayerModel(player_id=3)])
    with patch.object(MatchRepository, 'get_match', return_value=match):
        mock_db = mock_session.return_value
        mock_db.get.side_effect = [PlayerModel(player_id=4), match]
        mock_db.commit = MagicMock()
        mock_db.close = MagicMock()

        result = player_repo.assign_match_to_player(1, 1)

        mock_db.get.assert_any_call(PlayerModel, 1)
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
    match = MatchModel(player_count=4, players=[PlayerModel(player_id=1),
                                                PlayerModel(player_id=2), 
                                                PlayerModel(player_id=3), 
                                                PlayerModel(player_id=4)])
    with patch.object(MatchRepository, 'get_match', return_value=match):
        mock_db = mock_session.return_value
        mock_db.commit.side_effect = IntegrityError("mock", "mock", "mock")
        mock_db.close = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            player_repo.assign_match_to_player(1, 1)

        mock_db.get.assert_any_call(PlayerModel, 1)
        assert exc_info.value.detail == "Match is full."

def test_unassign_match_to_player(mock_session, player_repo):
    mock_db = mock_session.return_value
    mock_db.get.side_effect = [
        PlayerModel(player_id=1, match_id=1),
    ]
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    result = player_repo.unassign_match_to_player(1)

    mock_db.get.assert_any_call(PlayerModel, 1)
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()
    assert result is None

def test_delete_player(mock_session,player_repo):
    mock_db = mock_session.return_value
    mock_db.get.return_value = PlayerModel(player_id=1, match=MatchModel(player_count=1))
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    player = player_repo.delete_player(1)

    mock_db.get.assert_called_once_with(PlayerModel, 1)
    mock_db.commit.assert_called_once()
    assert player.player_id == 1