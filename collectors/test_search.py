import json

from utils.vlr_client import VLRClient

client = VLRClient()

queries = [
    "VCT 2025",
    "VCT 2024",
    "Champions 2024",
    "Masters Madrid",
    "Pacific 2025",
]

for query in queries:
    print("=" * 80)
    print(query)

    result = client.search(query)

    print(json.dumps(result, indent=2))