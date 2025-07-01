import os
import json
import requests
from dotenv import load_dotenv

# Load categories from .env
load_dotenv()
GROUPS_RAW = os.getenv("CHANNEL_GROUPS")
SOURCE_URL = os.environ.get("SOURCE_URL")  # from GitHub Secret

if not SOURCE_URL:
    raise ValueError("SOURCE_URL must be set as a GitHub Secret")

if not GROUPS_RAW:
    raise ValueError("CHANNEL_GROUPS must be defined in .env")

try:
    CHANNEL_GROUPS = json.loads(GROUPS_RAW.replace("'", '"'))
except json.JSONDecodeError as e:
    raise ValueError("Invalid CHANNEL_GROUPS format in .env") from e

# Fetch the playlist
try:
    response = requests.get(SOURCE_URL, timeout=10)
    response.raise_for_status()
    lines = response.text.splitlines()
except requests.RequestException as e:
    raise SystemExit(f"❌ Failed to fetch playlist: {e}")

# Filter and categorize
output = []
for i in range(len(lines)):
    if lines[i].startswith("#EXTINF"):
        name = lines[i].split(",")[-1].strip()
        url = lines[i+1] if i+1 < len(lines) else ""
        for cat, chan_list in CHANNEL_GROUPS.items():
            if name in chan_list:
                line = lines[i].replace("#EXTINF", f'#EXTINF:-1 group-title="{cat}"')
                output.append(line)
                output.append(url)
                break

# Save result
with open("Airtel.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("✅ Playlist categorized and saved successfully.")
