import sys

from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler

from exchanges import bittrex
from config import log
from . import WorkflowEnum, KeyboardEnum
from . import restrict_access, cancel, build_menu, keyboard_cmds, bold


def price_setup(dispatcher):
    # PRICE conversation handler
    price_handler = ConversationHandler(
        entry_points=[CommandHandler("price", price_cmd, pass_chat_data=True)],
        states={
            WorkflowEnum.PRICE_CURRENCY: [
                RegexHandler("^(CANCEL)$", cancel),
                RegexHandler("^/[A-Za-z0-9]+$", price_currency, pass_chat_data=True),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(price_handler)


# Show the last trade price for a currency
@restrict_access
def price_cmd(bot, update, chat_data):
    reply_msg = "Enter currency symbol against BTC eg. /XRP"
    try:
        cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

        reply_mrk = ReplyKeyboardMarkup(build_menu(cancel_btn), resize_keyboard=True)
        update.message.reply_text(
            reply_msg, reply_markup=reply_mrk, parse_mode=ParseMode.MARKDOWN
        )
    except:
        log.error("Error while getting price currency")
        return

    return WorkflowEnum.PRICE_CURRENCY


# Choose for which currency to show the last trade price
def price_currency(bot, update, chat_data):
    coin = update.message.text.upper()
    symbol = "BTC-{}".format(coin[1:])  # remove / from the start

    try:
        currency_price = bittrex.get_price(symbol)
        currency_price_message = "{}: {:06.8f}\n{}: {:06.8f}\n{}: {:06.8f}".format(
            bold("Ask"),
            currency_price.get("Ask"),
            bold("Bid"),
            currency_price.get("Bid"),
            bold("Last"),
            currency_price.get("Last"),
        )
        msg = "{}\n{}".format(bold(symbol), currency_price_message, symbol)
        update.message.reply_text(
            msg, reply_markup=keyboard_cmds(), parse_mode=ParseMode.MARKDOWN
        )
    except:
        update.message.reply_text(
            "Error while getting price currency {}".format(sys.exc_info())
        )
        return

    return ConversationHandler.END
