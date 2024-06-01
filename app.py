import json

with open("all_links.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(len(data))
