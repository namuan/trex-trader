from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

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
    coin_buttons_from_list,
    percent_change_buttons,
)


def sell_setup(dispatcher):
    # SELL conversation handler
    chart_handler = ConversationHandler(
        entry_points=[CommandHandler("sell", sell_cmd, pass_chat_data=True)],
        states={
            WorkflowEnum.TRADE_CALCULATE_SELL_COST: [
                MessageHandler(
                    Filters.regex("^(" + regex_coin(market_summary_alt_coins()) + ")$"),
                    calculate_sell_order_size,
                    pass_chat_data=True,
                ),
                MessageHandler(Filters.regex("^(CANCEL)$"), cancel),
            ],
            WorkflowEnum.TRADE_CHANGE_SELL_PRICE: [
                MessageHandler(
                    Filters.regex("^\+(\d+)\%$"),
                    change_sell_price,
                    pass_chat_data=True,
                ),
                MessageHandler(
                    Filters.regex("^([\d\.]+)\s+([\d\.]+)$"),
                    change_sell_price,
                    pass_chat_data=True,
                ),
                MessageHandler(
                    Filters.regex("^(SELL)$"), place_sell_order, pass_chat_data=True
                ),
                MessageHandler(Filters.regex("^(CANCEL)$"), cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(chart_handler)


@restrict_access
def sell_cmd(update, context):
    reply_msg = "Choose currency"

    alt_wallets = [
        w.get("currency") for w in bittrex.get_balances() if w.get("currency") != "BTC"
    ]

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

    reply_mrk = ReplyKeyboardMarkup(
        build_menu(
            coin_buttons_from_list(alt_wallets), n_cols=3, footer_buttons=cancel_btn
        ),
        resize_keyboard=True,
    )
    update.message.reply_text(reply_msg, reply_markup=reply_mrk)

    return WorkflowEnum.TRADE_CALCULATE_SELL_COST


def calculate_sell_order_size(update, context):
    currency = update.message.text
    coin_symbol = "BTC-{}".format(currency)

    price_info = bittrex.get_price(coin_symbol)
    if not price_info:
        return cancel(
            update, context, text="Unable to retrieve price for {}".format(coin_symbol)
        )

    bid_price = price_info.get("Bid")

    available_in_balance = get_all_from_balance(currency)

    if not available_in_balance:
        return cancel(
            update,
            "You do not have any coins available for {} in your wallet".format(
                currency
            ),
        )

    _, commission, total = bittrex.trade_commission(available_in_balance, bid_price)

    reply_msg = (
        "{} bid is *{:06.8f}*\n"
        "order size is *{:06.8f}*.\n"
        "Exchange commission will be *{:06.8f}*.\n"
        "Total price: *{:06.8f}*\n"
        "Change order sell price using the options below or place the order".format(
            coin_symbol, bid_price, available_in_balance, commission, total
        )
    )

    buttons = percent_change_buttons()
    buttons.append(KeyboardButton(KeyboardEnum.SELL.clean()))

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

    context.user_data["coin_symbol"] = coin_symbol
    context.user_data["quantity_to_sell"] = available_in_balance
    context.user_data["sell_price"] = bid_price

    reply_mrk = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2, footer_buttons=cancel_btn), resize_keyboard=True
    )
    update.message.reply_text(
        reply_msg, reply_markup=reply_mrk, parse_mode=ParseMode.MARKDOWN
    )

    return WorkflowEnum.TRADE_CHANGE_SELL_PRICE


def change_sell_price(update, context, groups):
    coin_symbol = context.user_data.get("coin_symbol")
    quantity_to_sell = context.user_data.get("quantity_to_sell")
    sell_price = context.user_data.get("sell_price")

    if len(groups) > 1:  # manual quantity and price entry
        quantity_to_sell = float(groups[0])
        new_sell_price = float(groups[1])
    else:
        percent_change = float(groups[0])
        new_sell_price = sell_price + sell_price * (percent_change / 100)

    _, commission, total = bittrex.trade_commission(quantity_to_sell, new_sell_price)

    reply_msg = (
        "{} *new* bid is *{:06.8f}*\n"
        "order size is *{:06.8f}*.\n"
        "Exchange commission will be *{:06.8f}*.\n"
        "Total price: *{:06.8f}*\n"
        "Change order sell price using the options below or place the order".format(
            coin_symbol, new_sell_price, quantity_to_sell, commission, total
        )
    )

    buttons = percent_change_buttons()
    buttons.append(KeyboardButton(KeyboardEnum.SELL.clean()))

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]

    context.user_data["coin_symbol"] = coin_symbol
    context.user_data["quantity_to_sell"] = quantity_to_sell
    context.user_data["sell_price"] = new_sell_price

    reply_mrk = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2, footer_buttons=cancel_btn), resize_keyboard=True
    )
    update.message.reply_text(
        reply_msg, reply_markup=reply_mrk, parse_mode=ParseMode.MARKDOWN
    )

    return WorkflowEnum.TRADE_CHANGE_SELL_PRICE


def place_sell_order(update, context):
    coin_symbol = context.user_data.get("coin_symbol")
    quantity_to_sell = "{:06.4f}".format(context.user_data.get("quantity_to_sell"))
    sell_price = "{:06.8f}".format(context.user_data.get("sell_price"))

    order_id = bittrex.sell_order(
        quantity_to_sell=quantity_to_sell,
        trade_symbol=coin_symbol,
        sell_price=float(sell_price),
    )

    reply_msg = "Selling {} of {} at {}\nOrder Id: {}".format(
        quantity_to_sell, coin_symbol, sell_price, order_id
    )

    update.message.reply_text(reply_msg, reply_markup=keyboard_cmds())
    return ConversationHandler.END


def get_all_from_balance(currency):
    bittrex_balances = bittrex.get_balances()
    return next(
        (c.get("available") for c in bittrex_balances if c.get("currency") == currency),
        None,
    )
