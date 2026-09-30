import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID"))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = "custom_bot"
