import sys

from telegram import ParseMode

from common import *
from exchanges import bittrex
from . import restrict_access


# Get balance of all currencies
@restrict_access
def wallets_cmd(bot, update, chat_data):
    wallets_msg = check_wallets()
    update.message.reply_text(wallets_msg, parse_mode=ParseMode.MARKDOWN)


def check_wallets():
    try:
        all_wallets = [w for w in bittrex.get_balances()]

        dt = datetime_now()
        combined_balance_message = ["🗓 #Wallets ({})".format(dt)]

        for w in all_wallets:
            currency = w.get('currency')
            available_alts = w.get('available')

            msg = "*{}* ({})".format(
                currency,
                available_alts
            )
            combined_balance_message.append(msg)

        return "\n".join(combined_balance_message)
    except:
        error_msg = "🚨 Error getting wallets." \
                    "See logs for more info. " \
                    "Exception details: {}".format(
            sys.exc_info())
        return error_msg
