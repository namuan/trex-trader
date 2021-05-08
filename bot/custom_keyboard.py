from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ConversationHandler

from config import market_summary_alt_coins
from . import KeyboardEnum


# Custom keyboard that shows all available commands
def keyboard_cmds():
    command_buttons = [
        KeyboardButton("/wallets"),
        KeyboardButton("/market"),
        KeyboardButton("/buy"),
        KeyboardButton("/sell"),
        KeyboardButton("/orders"),
    ]

    return ReplyKeyboardMarkup(
        build_menu(command_buttons, n_cols=3), resize_keyboard=True
    )


# Generic custom keyboard that shows YES and NO
def keyboard_confirm():
    buttons = [
        KeyboardButton(KeyboardEnum.YES.clean()),
        KeyboardButton(KeyboardEnum.NO.clean()),
    ]

    return ReplyKeyboardMarkup(build_menu(buttons, n_cols=2), resize_keyboard=True)


def keyboard_buy_sell():
    buttons = [
        KeyboardButton(KeyboardEnum.BUY.clean()),
        KeyboardButton(KeyboardEnum.SELL.clean()),
    ]

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

    return ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2, footer_buttons=cancel_btn), resize_keyboard=True
    )


# Create a button menu to show in Telegram messages
def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]

    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)

    return menu


# Create a list with a button for every coin in config
def coin_buttons():
    return coin_buttons_from_list(market_summary_alt_coins())


def coin_buttons_from_list(button_list):
    buttons = list()

    for coin in button_list:
        buttons.append(KeyboardButton(coin))

    return buttons


# Will show a cancel message, end the conversation and show the default keyboard
def cancel(update, context, text="Cancelled..."):
    update.message.reply_text(text, reply_markup=keyboard_cmds())
    return ConversationHandler.END
