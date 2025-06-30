import re
import os
from dotenv import load_dotenv
import requests

# === LOAD ENV ===
load_dotenv()
SOURCE_URL = os.getenv("SOURCE_URL")
CHANNELS = os.getenv("CHANNELS", "")

if not SOURCE_URL:
    print("❌ SOURCE_URL not set in .env")
    exit()

selected_channels = [c.strip().lower() for c in CHANNELS.split(",") if c.strip()]

# === FETCH FRESH DATA ===
print(f"📥 Fetching from {SOURCE_URL}")
try:
    r = requests.get(SOURCE_URL)
    r.raise_for_status()
except Exception as e:
    print(f"❌ Failed to fetch source: {e}")
    exit()

lines = r.text.splitlines()
fresh_blocks = []

# === EXTRACT ONLY SELECTED CHANNEL BLOCKS ===
i = 0
while i < len(lines) - 2:
    if lines[i].startswith("#EXTINF:") and any(ch.lower() in lines[i].lower() for ch in selected_channels):
        if lines[i+1].startswith("#EXTHTTP:") and lines[i+2].startswith("http"):
            fresh_blocks.append((lines[i], lines[i+1], lines[i+2]))
            i += 3
            continue
    i += 1

if not fresh_blocks:
    print("❌ No matching channels found.")
    exit()

print(f"✅ Found {len(fresh_blocks)} selected channels.")

# === BUILD UPDATED PLAYLIST ===
header = "#EXTM3U\n# Updated by GitHub Action\n\n"
new_content = header
for block in fresh_blocks:
    new_content += block[0] + "\n"  # EXTINF
    new_content += block[1] + "\n"  # EXTHTTP
    new_content += block[2] + "\n"  # URL

# === WRITE TO FILE ===
with open("artl.m3u", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ artl.m3u written with selected channels only.")
