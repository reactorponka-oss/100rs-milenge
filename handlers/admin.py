from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_ID
from database import (
    get_settings, update_settings,
    add_button, get_all_buttons, get_button,
    update_button_field, delete_button,
    add_channel, get_all_channels, delete_channel,
    get_all_users
)

(
    ADMIN_MENU,
    WAIT_WELCOME_TEXT, WAIT_WELCOME_PHOTO,
    WAIT_BTN_NAME, WAIT_BTN_TYPE, WAIT_BTN_VALUE,
    WAIT_EDIT_VALUE,
    WAIT_CHANNEL_ID, WAIT_CHANNEL_NAME, WAIT_CHANNEL_LINK,
    WAIT_BROADCAST
) = range(11)


def is_admin(uid):
    return uid == ADMIN_ID


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Welcome Text", callback_data="a_wtext"),
         InlineKeyboardButton("🖼️ Welcome Photo", callback_data="a_wphoto")],
        [InlineKeyboardButton("🔁 Force Join ON/OFF", callback_data="a_fj_toggle")],
        [InlineKeyboardButton("➕ Add Button", callback_data="a_addbtn"),
         InlineKeyboardButton("📋 Manage Buttons", callback_data="a_mngbtn")],
        [InlineKeyboardButton("📢 Add Channel", callback_data="a_addch"),
         InlineKeyboardButton("📋 Manage Channels", callback_data="a_mngch")],
        [InlineKeyboardButton("📣 Broadcast", callback_data="a_broadcast")],
    ])


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("🔧 Admin Panel", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "a_wtext":
        await q.edit_message_text("Naya welcome text bhej:")
        return WAIT_WELCOME_TEXT

    if d == "a_wphoto":
        await q.edit_message_text("Nayi welcome photo bhej:")
        return WAIT_WELCOME_PHOTO

    if d == "a_fj_toggle":
        s = await get_settings()
        new_val = not s.get("force_join", False)
        await update_settings("force_join", new_val)
        await q.edit_message_text(
            f"✅ Force Join ab {'ON' if new_val else 'OFF'} hai.",
            reply_markup=main_menu_kb()
        )
        return ADMIN_MENU

    if d == "a_addbtn":
        context.user_data.pop("edit_btn_id", None)
        await q.edit_message_text("Naye button ka naam bhej:")
        return WAIT_BTN_NAME

    if d == "a_mngbtn":
        btns = await get_all_buttons()
        if not btns:
            await q.edit_message_text("Koi button nahi.", reply_markup=main_menu_kb())
            return ADMIN_MENU
        kb = [[InlineKeyboardButton(f"⚙️ {b['name']}", callback_data=f"mng_{b['_id']}")] for b in btns]
        kb.append([InlineKeyboardButton("⬅️ Back", callback_data="a_back")])
        await q.edit_message_text("Kaunsa button?", reply_markup=InlineKeyboardMarkup(kb))
        return ADMIN_MENU

    if d.startswith("mng_"):
        btn_id = d.replace("mng_", "")
        btn = await get_button(btn_id)
        if not btn:
            await q.edit_message_text("Nahi mila.", reply_markup=main_menu_kb())
            return ADMIN_MENU
        context.user_data["edit_btn_id"] = btn_id
        kb = [
            [InlineKeyboardButton("✏️ Naam Badlo", callback_data="eb_name")],
            [InlineKeyboardButton("🔁 Action Badlo", callback_data="eb_action")],
            [InlineKeyboardButton("🗑️ Delete", callback_data="eb_delete")],
            [InlineKeyboardButton("⬅️ Back", callback_data="a_back")],
        ]
        await q.edit_message_text(
            f"Button: {btn['name']}\nType: {btn['action_type']}\nValue: {btn['action_value']}",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return ADMIN_MENU

    if d == "eb_name":
        await q.edit_message_text("Naya naam bhej:")
        return WAIT_BTN_NAME

    if d == "eb_action":
        kb = [
            [InlineKeyboardButton("Text Reply", callback_data="et_text")],
            [InlineKeyboardButton("Photo Reply", callback_data="et_photo")],
            [InlineKeyboardButton("URL", callback_data="et_url")],
        ]
        await q.edit_message_text("Naya type:", reply_markup=InlineKeyboardMarkup(kb))
        return WAIT_BTN_TYPE

    if d == "eb_delete":
        await delete_button(context.user_data["edit_btn_id"])
        context.user_data.pop("edit_btn_id", None)
        await q.edit_message_text("✅ Delete ho gaya.", reply_markup=main_menu_kb())
        return ADMIN_MENU

    if d.startswith("et_"):
        context.user_data["edit_type"] = d.replace("et_", "")
        await q.edit_message_text("Nayi value bhej:")
        return WAIT_EDIT_VALUE

    if d == "a_addch":
        await q.edit_message_text("Channel ID bhej (-100...):")
        return WAIT_CHANNEL_ID

    if d == "a_mngch":
        chs = await get_all_channels()
        if not chs:
            await q.edit_message_text("Koi channel nahi.", reply_markup=main_menu_kb())
            return ADMIN_MENU
        kb = [[InlineKeyboardButton(f"❌ {c['name']}", callback_data=f"delch_{c['channel_id']}")] for c in chs]
        kb.append([InlineKeyboardButton("⬅️ Back", callback_data="a_back")])
        await q.edit_message_text("Delete karne ke liye click:", reply_markup=InlineKeyboardMarkup(kb))
        return ADMIN_MENU

    if d.startswith("delch_"):
        await delete_channel(int(d.replace("delch_", "")))
        await q.edit_message_text("✅ Delete.", reply_markup=main_menu_kb())
        return ADMIN_MENU

    if d == "a_broadcast":
        await q.edit_message_text("Broadcast message bhej (text/photo):")
        return WAIT_BROADCAST

    if d == "a_back":
        await q.edit_message_text("🔧 Admin Panel", reply_markup=main_menu_kb())
        return ADMIN_MENU

    return ADMIN_MENU


async def set_welcome_text(update, context):
    await update_settings("welcome_text", update.message.text)
    await update.message.reply_text("✅ Done.", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def set_welcome_photo(update, context):
    if not update.message.photo:
        await update.message.reply_text("Photo bhej.")
        return WAIT_WELCOME_PHOTO
    await update_settings("welcome_photo", update.message.photo[-1].file_id)
    await update.message.reply_text("✅ Done.", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def set_btn_name(update, context):
    if context.user_data.get("edit_btn_id"):
        await update_button_field(context.user_data["edit_btn_id"], "name", update.message.text)
        context.user_data.pop("edit_btn_id", None)
        await update.message.reply_text("✅ Naam update.", reply_markup=main_menu_kb())
        return ADMIN_MENU

    context.user_data["new_btn_name"] = update.message.text
    kb = [
        [InlineKeyboardButton("Text Reply", callback_data="nt_text")],
        [InlineKeyboardButton("Photo Reply", callback_data="nt_photo")],
        [InlineKeyboardButton("URL", callback_data="nt_url")],
    ]
    await update.message.reply_text("Type choose kar:", reply_markup=InlineKeyboardMarkup(kb))
    return WAIT_BTN_TYPE


async def set_btn_type(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["new_btn_type"] = q.data.replace("nt_", "")
    await q.edit_message_text("Value bhej:")
    return WAIT_BTN_VALUE


async def set_btn_value(update, context):
    val = update.message.text if update.message.text else ""
    if update.message.photo and context.user_data.get("new_btn_type") == "photo":
        val = update.message.photo[-1].file_id
    await add_button(
        context.user_data["new_btn_name"],
        context.user_data["new_btn_type"],
        val
    )
    await update.message.reply_text("✅ Button add.", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def set_edit_value(update, context):
    val = update.message.text if update.message.text else ""
    if update.message.photo:
        val = update.message.photo[-1].file_id
    bid = context.user_data["edit_btn_id"]
    await update_button_field(bid, "action_type", context.user_data["edit_type"])
    await update_button_field(bid, "action_value", val)
    context.user_data.pop("edit_btn_id", None)
    await update.message.reply_text("✅ Update.", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def set_channel_id(update, context):
    try:
        context.user_data["ch_id"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Galat ID. Fir se bhej:")
        return WAIT_CHANNEL_ID
    await update.message.reply_text("Channel ka naam:")
    return WAIT_CHANNEL_NAME


async def set_channel_name(update, context):
    context.user_data["ch_name"] = update.message.text
    await update.message.reply_text("Invite link bhej:")
    return WAIT_CHANNEL_LINK


async def set_channel_link(update, context):
    await add_channel(
        context.user_data["ch_id"],
        context.user_data["ch_name"],
        update.message.text
    )
    await update.message.reply_text("✅ Channel add.", reply_markup=main_menu_kb())
    return ADMIN_MENU


async def broadcast_handler(update, context):
    users = await get_all_users()
    sent = 0
    msg = update.message
    for u in users:
        try:
            if msg.photo:
                await context.bot.send_photo(u["user_id"], msg.photo[-1].file_id,
                                             caption=msg.caption or "")
            elif msg.text:
                await context.bot.send_message(u["user_id"], msg.text)
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcast {sent} users ko gaya.", reply_markup=main_menu_kb())
    return ADMIN_MENU
