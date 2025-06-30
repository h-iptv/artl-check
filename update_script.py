import re
import os
from dotenv import load_dotenv
import requests

# === Load .env ===
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

print(f"📥 Fetching playlist from: {SOURCE_URL}")
try:
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
except Exception as e:
    print(f"❌ Error fetching playlist: {e}")
    exit()

# === Parse full blocks ===
full_blocks = []
i = 0
while i < len(lines) - 5:
    if lines[i].startswith("#KODIPROP:") and \
       lines[i+1].startswith("#KODIPROP:") and \
       lines[i+2].startswith("#EXTINF:") and \
       lines[i+3].startswith("#EXTHTTP:") and \
       lines[i+4].startswith("#EXTVLCOPT:") and \
       lines[i+5].startswith("http"):
        
        extinf = lines[i+2]
        if any(ch in extinf.lower() for ch in selected_channels):
            block = "\n".join(lines[i:i+6])
            full_blocks.append(block)
            i += 6
            continue
    i += 1

# === Write updated playlist ===
output_file = "artl.m3u"
if full_blocks:
    print(f"✅ Found {len(full_blocks)} matching channel(s)")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated by GitHub Action\n\n")
        for block in full_blocks:
            f.write(block + "\n")
else:
    print("⚠️ No matching channels found. Creating empty playlist.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# No matching channels found\n")

# === Set write permissions just in case
os.chmod(output_file, 0o666)
print(f"✅ '{output_file}' written successfully.")
