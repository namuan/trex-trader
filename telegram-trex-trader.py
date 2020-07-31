#!/usr/bin/python3
"""
python3.6 telegram-trex-trader.py
"""
from telegram import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler

from bot import *


def handle_inline_option(bot, update, chat_data):
    query = update.callback_query
    oo = chat_data[query.data]
    chat_data["selected_order"] = query.data
    bot.edit_message_text(
        text="Selected order:\n{}. Press /cancel to cancel order".format(
            oo.get("order_text")
        ),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        parse_mode=ParseMode.MARKDOWN,
    )


dispatcher.add_error_handler(handle_telegram_error)

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start_cmd))
dispatcher.add_handler(CommandHandler("restart", restart_cmd, pass_chat_data=True))
dispatcher.add_handler(CommandHandler("shutdown", shutdown_cmd, pass_chat_data=True))
dispatcher.add_handler(CommandHandler("wallets", wallets_cmd, pass_chat_data=True))

updater.dispatcher.add_handler(
    CallbackQueryHandler(handle_inline_option, pass_chat_data=True)
)

buy_setup(dispatcher)
sell_setup(dispatcher)
open_order_setup(dispatcher)
cancel_order_setup(dispatcher)
market_info_setup(dispatcher)

updater.start_polling()

start_cmd(updater)

updater.idle()
