from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler

from exchanges import bittrex
from . import restrict_access, keyboard_cmds


def open_order_setup(dispatcher):
    # ORDER conversation handler
    dispatcher.add_handler(CommandHandler("orders", open_order_cmd, pass_chat_data=True))


# Show the last trade price for a currency
@restrict_access
def open_order_cmd(bot, update, chat_data):
    open_orders = bittrex.get_open_orders()
    if not open_orders:
        update.message.reply_text('No open orders found', reply_markup=keyboard_cmds())
        return

    inline_keyboards = []
    select_order_text = []
    for idx, oo in enumerate(open_orders):
        exchange = oo.get('Exchange')
        order_type = oo.get('OrderType').replace('LIMIT_', '')
        quantity = oo.get('Quantity')
        limit = oo.get('Limit')
        order_id = oo.get('OrderUuid')
        order_text = "{} _{}_ [{}](https://bittrex.com/Market/Index?MarketName={}) at {:06.8f}".format(
            order_type,
            quantity,
            exchange,
            exchange,
            limit
        )
        select_order_text.append("*{}*: {}".format(idx + 1, order_text))
        oo['order_text'] = order_text
        chat_data[order_id] = oo
        inline_keyboards.append(
            InlineKeyboardButton(idx + 1, callback_data=order_id)
        )

    reply_markup = InlineKeyboardMarkup([inline_keyboards])

    all_open_orders_text = "\n".join(select_order_text)
    update.message.reply_text(
        "{}\n.Please select order number from above:".format(all_open_orders_text),
        reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END
