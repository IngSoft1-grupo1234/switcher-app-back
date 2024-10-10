import requests

BASE_URL = "http://localhost:8000"


player_ids = []
for i in range(4):
    player_response = requests.post(f"{BASE_URL}/players", json={"username": f"Player {i+1}"})
    player_ids.append(player_response.json()["player_id"])

first_player_id = player_ids[0]
match_data = {
    "match_name": "Test Match",
    "max_players": 4,
    "host": first_player_id
}

match_response = requests.post(f"{BASE_URL}/matches", json=match_data)
match_id = match_response.json()["match_id"]




for player_id in player_ids:
    if player_id != first_player_id:
        requests.put(f"{BASE_URL}/players/{player_id}/AssignToMatch/{match_id}")

requests.put(f"{BASE_URL}/matches/{match_id}/start")

print("Match creada y jugadores asignados correctamente")
