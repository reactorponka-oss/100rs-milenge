import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN
from database import init_db
from handlers.user import start, check_join_callback
from handlers.callbacks import button_click
from handlers.admin import (
    admin_panel, admin_callback,
    set_welcome_text, set_welcome_photo,
    set_btn_name, set_btn_type, set_btn_value, set_edit_value,
    set_channel_id, set_channel_name, set_channel_link,
    broadcast_handler,
    ADMIN_MENU, WAIT_WELCOME_TEXT, WAIT_WELCOME_PHOTO,
    WAIT_BTN_NAME, WAIT_BTN_TYPE, WAIT_BTN_VALUE, WAIT_EDIT_VALUE,
    WAIT_CHANNEL_ID, WAIT_CHANNEL_NAME, WAIT_CHANNEL_LINK,
    WAIT_BROADCAST
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(app):
    await init_db()


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))

    conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADMIN_MENU: [CallbackQueryHandler(admin_callback)],
            WAIT_WELCOME_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_welcome_text)],
            WAIT_WELCOME_PHOTO: [MessageHandler(filters.PHOTO, set_welcome_photo)],
            WAIT_BTN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_btn_name)],
            WAIT_BTN_TYPE: [CallbackQueryHandler(set_btn_type, pattern="^nt_")],
            WAIT_BTN_VALUE: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, set_btn_value)],
            WAIT_EDIT_VALUE: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, set_edit_value)],
            WAIT_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_channel_id)],
            WAIT_CHANNEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_channel_name)],
            WAIT_CHANNEL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_channel_link)],
            WAIT_BROADCAST: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, broadcast_handler)],
        },
        fallbacks=[CommandHandler("admin", admin_panel)],
        per_message=False,
    )
    app.add_handler(conv)

    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(button_click, pattern="^btn_"))

    print("✅ Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
