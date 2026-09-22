from utils.vlr_client import VLRClient

client = VLRClient()

events = client.get_events()

print(events["status"])
print(len(events["data"]["segments"]))

print(events["data"]["segments"][0])