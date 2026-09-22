import requests


class VLRClient:
    def __init__(self):
        self.base_url = "http://127.0.0.1:3001"

    def get_events(self):
        response = requests.get(f"{self.base_url}/v2/events")
        response.raise_for_status()
        return response.json()

    def get_event_matches(self, event_id):
        response = requests.get(
            f"{self.base_url}/v2/events/matches",
            params={"event_id": event_id}
        )
        response.raise_for_status()
        return response.json()

    def get_match_details(self, match_id):
        response = requests.get(
            f"{self.base_url}/v2/match/details",
            params={"match_id": match_id}
        )
        response.raise_for_status()
        return response.json()

    def search(self, query):
        response = requests.get(
            f"{self.base_url}/v2/search",
            params={"q": query}
        )
        response.raise_for_status()
        return response.json()