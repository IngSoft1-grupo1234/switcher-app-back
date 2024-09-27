from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_player():
    response = client.post(
        "/players/",
        json={"username": "john"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "playername" : "john",
        "playerId": 0
    }