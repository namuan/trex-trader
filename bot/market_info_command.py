from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler

from config import market_summary_alt_coins
from exchanges import bittrex
from . import (
    WorkflowEnum,
    KeyboardEnum,
    restrict_access,
    build_menu,
    keyboard_cmds,
    cancel,
    regex_coin,
    coin_buttons,
)


def market_info_setup(dispatcher):
    # MARKET INFO conversation handler
    chart_handler = ConversationHandler(
        entry_points=[CommandHandler("market", market_info_cmd, pass_chat_data=True)],
        states={
            WorkflowEnum.MARKET_INFO: [
                RegexHandler(
                    "^(" + regex_coin(market_summary_alt_coins()) + ")$",
                    send_market_info_msg,
                    pass_chat_data=True,
                ),
                RegexHandler("^(CANCEL)$", cancel),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(chart_handler)


@restrict_access
def market_info_cmd(bot, update, chat_data):
    reply_msg = "Choose currency"

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

    reply_mrk = ReplyKeyboardMarkup(
        build_menu(coin_buttons(), n_cols=3, footer_buttons=cancel_btn),
        resize_keyboard=True,
    )
    update.message.reply_text(reply_msg, reply_markup=reply_mrk)

    return WorkflowEnum.MARKET_INFO


def send_market_info_msg(bot, update, chat_data):
    currency = update.message.text
    pair_symbol = "BTC-{}".format(currency)
    market_data_msg = format_price_data(pair_symbol)

    reply_msg = "💹 Market info [{0}](https://bittrex.com/Market/Index?MarketName={0})\n{1}\n".format(
        pair_symbol, market_data_msg
    )

    update.message.reply_text(
        reply_msg, reply_markup=keyboard_cmds(), parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


def format_price_data(symbol):
    data = bittrex.get_price(symbol)
    return "Last {:06.8f}".format(data.get("Last"))
