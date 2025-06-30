import re
import os
from dotenv import load_dotenv
import requests

# === Load .env file ===
load_dotenv()
SOURCE_URL = os.getenv("SOURCE_URL")
CHANNELS = os.getenv("CHANNELS", "")

if not SOURCE_URL:
    print("❌ SOURCE_URL is missing in .env")
    exit()

selected_channels = [ch.strip().lower() for ch in CHANNELS.split(",") if ch.strip()]
if not selected_channels:
    print("❌ No CHANNELS defined in .env")
    exit()

print(f"📥 Fetching fresh playlist from: {SOURCE_URL}")
try:
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    fresh_lines = response.text.splitlines()
except Exception as e:
    print(f"❌ Error fetching playlist: {e}")
    exit()

# === Extract selected channel blocks ===
fresh_blocks = []
i = 0
while i < len(fresh_lines) - 2:
    line = fresh_lines[i]
    if line.startswith("#EXTINF:") and any(ch in line.lower() for ch in selected_channels):
        if fresh_lines[i+1].startswith("#EXTHTTP:") and fresh_lines[i+2].startswith("http"):
            fresh_blocks.append((line, fresh_lines[i+1], fresh_lines[i+2]))
            i += 3
            continue
    i += 1

# === Write output ===
output_file = "artl.m3u"
header = "#EXTM3U\n# Updated by GitHub Action\n\n"

if fresh_blocks:
    print(f"✅ Found {len(fresh_blocks)} matching channel(s)")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header)
        for block in fresh_blocks:
            f.write(block[0] + "\n")
            f.write(block[1] + "\n")
            f.write(block[2] + "\n")
else:
    print("⚠️ No matching channels found, creating empty playlist.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# No matching channels found\n")

# === Ensure file is writable ===
os.chmod(output_file, 0o666)
print(f"✅ '{output_file}' written successfully.")
