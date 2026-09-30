from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_settings, get_all_buttons, save_user, get_all_channels


async def is_joined(bot, user_id):
    channels = await get_all_channels()
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["channel_id"], user_id)
            if member.status in ("left", "kicked"):
                return False, ch
        except Exception:
            return False, ch
    return True, None


def join_kb(channels):
    kb = [[InlineKeyboardButton(f"📢 Join {c['name']}", url=c["invite_link"])] for c in channels]
    kb.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])
    return InlineKeyboardMarkup(kb)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)

    settings = await get_settings()

    if settings.get("force_join"):
        joined, _ = await is_joined(context.bot, user.id)
        if not joined:
            channels = await get_all_channels()
            if update.message:
                await update.message.reply_text(
                    "⚠️ Bot use karne ke liye pehle in channels ko join karo:",
                    reply_markup=join_kb(channels)
                )
            return

    buttons = await get_all_buttons()
    kb = []
    for b in buttons:
        if b["action_type"] == "url":
            kb.append([InlineKeyboardButton(b["name"], url=b["action_value"])])
        else:
            kb.append([InlineKeyboardButton(b["name"], callback_data=f"btn_{b['_id']}")])

    markup = InlineKeyboardMarkup(kb) if kb else None
    text = settings.get("welcome_text", "Welcome!")
    photo = settings.get("welcome_photo")

    if update.message:
        if photo:
            await update.message.reply_photo(photo=photo, caption=text, reply_markup=markup)
        else:
            await update.message.reply_text(text, reply_markup=markup)


async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    joined, ch = await is_joined(context.bot, q.from_user.id)
    if not joined:
        await q.answer(f"❌ Pehle {ch['name']} join karo!", show_alert=True)
        return
    await q.message.delete()
    await start(update, context)
