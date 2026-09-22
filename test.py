import requests
import json

BASE_URL = "http://127.0.0.1:3001"

response = requests.get(
    f"{BASE_URL}/v2/match/details",
    params={"match_id": "701025"}
)

print(response.url)
print(response.status_code)
print(json.dumps(response.json(), indent=2))