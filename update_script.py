import os
import re
import json
import requests
from dotenv import load_dotenv

# === Load env variables from .env ===
load_dotenv()

# === Load SOURCE_URL from environment (e.g., GitHub Secrets) ===
SOURCE_URL = os.environ.get("SOURCE_URL")
CHANNEL_GROUPS_RAW = os.getenv("CHANNEL_GROUPS")

if not SOURCE_URL:
    print("❌ SOURCE_URL is not set in GitHub Secrets or environment.")
    exit()

if not CHANNEL_GROUPS_RAW:
    print("❌ CHANNEL_GROUPS is not set in .env")
    exit()

# Parse CHANNEL_GROUPS JSON string
try:
    channel_groups = json.loads(CHANNEL_GROUPS_RAW)
except json.JSONDecodeError as e:
    print(f"❌ Invalid CHANNEL_GROUPS format: {e}")
    exit()

# Build lookup for allowed channels
allowed_channels = {}
for group, channels in channel_groups.items():
    for name in channels:
        allowed_channels[name.lower()] = group  # Map lowercase name to group

# === Fetch playlist ===
print(f"📥 Fetching playlist from: {SOURCE_URL}")
try:
    response = requests.get(SOURCE_URL, timeout=20)
    response.raise_for_status()
    lines = response.text.splitlines()
except Exception as e:
    print(f"❌ Error fetching playlist: {e}")
    exit()

# === Process full 6-line channel blocks ===
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
        try:
            channel_name = extinf.split(",")[-1].strip()
            group = allowed_channels.get(channel_name.lower())
        except:
            group = None

        if group:
            # Inject updated group-title into EXTINF
            updated_extinf = re.sub(r'group-title=".*?"', f'group-title="{group}"', extinf)
            block = "\n".join([
                lines[i],
                lines[i+1],
                updated_extinf,
                lines[i+3],
                lines[i+4],
                lines[i+5]
            ])
            full_blocks.append(block)
            i += 6
            continue
    i += 1

# === Write output
output_file = "Airtel.m3u"
if os.path.exists(output_file):
    os.remove(output_file)

with open(output_file, "w", encoding="utf-8") as f:
    if full_blocks:
        print(f"✅ Found {len(full_blocks)} categorized channels.")
        f.write("#EXTM3U\n# Updated By Himanshu\n\n")
        for block in full_blocks:
            f.write(block + "\n")
    else:
        print("⚠️ No matching channels found.")
        f.write("#EXTM3U\n# No matching channels found\n")

os.chmod(output_file, 0o666)
print(f"✅ '{output_file}' written with category assignments.")
