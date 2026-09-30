from telegram import Update
from telegram.ext import ContextTypes
from database import get_button


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("btn_"):
        return
    btn = await get_button(data.replace("btn_", ""))
    if not btn:
        await q.message.reply_text("Button nahi mila.")
        return
    t = btn["action_type"]
    v = btn["action_value"]
    if t == "text":
        await q.message.reply_text(v)
    elif t == "photo":
        await q.message.reply_photo(photo=v)
    elif t == "url":
        await q.message.reply_text(v)
