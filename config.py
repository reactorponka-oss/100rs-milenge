import os
from dotenv import load_dotenv

load_dotenv()

# ---------- Bot ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- Admins (multiple) ----------
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()]

# ---------- Database ----------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = "custom_bot"

# ---------- Startup Checks ----------
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN missing! Environment variable set karo.")

if not ADMIN_IDS:
    raise ValueError("❌ ADMIN_IDS missing or empty! Comma-separated IDs daalo.")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI missing! Environment variable set karo.")

print(f"✅ Config loaded. Admins: {ADMIN_IDS}")
