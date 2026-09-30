from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

settings_col = db["settings"]
buttons_col  = db["buttons"]
channels_col = db["channels"]
users_col    = db["users"]


async def init_db():
    if not await settings_col.find_one({"_id": "config"}):
        await settings_col.insert_one({
            "_id": "config",
            "welcome_text": "Welcome to the bot!",
            "welcome_photo": None,
            "force_join": False,
        })


async def get_settings():
    return await settings_col.find_one({"_id": "config"})


async def update_settings(field, value):
    await settings_col.update_one({"_id": "config"}, {"$set": {field: value}})


async def add_button(name, action_type, action_value):
    count = await buttons_col.count_documents({})
    await buttons_col.insert_one({
        "name": name,
        "action_type": action_type,
        "action_value": action_value,
        "order": count,
    })


async def get_all_buttons():
    return await buttons_col.find().sort("order", 1).to_list(length=200)


async def get_button(btn_id):
    return await buttons_col.find_one({"_id": ObjectId(btn_id)})


async def update_button_field(btn_id, field, value):
    await buttons_col.update_one({"_id": ObjectId(btn_id)}, {"$set": {field: value}})


async def delete_button(btn_id):
    await buttons_col.delete_one({"_id": ObjectId(btn_id)})


async def add_channel(channel_id, name, invite_link):
    await channels_col.insert_one({
        "channel_id": channel_id,
        "name": name,
        "invite_link": invite_link,
    })


async def get_all_channels():
    return await channels_col.find().to_list(length=50)


async def delete_channel(channel_id):
    await channels_col.delete_one({"channel_id": channel_id})


async def save_user(user_id):
    await users_col.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id}},
        upsert=True
    )


async def get_all_users():
    return await users_col.find().to_list(length=100000)
