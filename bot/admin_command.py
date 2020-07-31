import os
import sys
import threading
import time

from telegram import ReplyKeyboardRemove

from config import bot_cfg
from . import keyboard_cmds, updater
from . import restrict_access


# This needs to be run on a new thread because calling 'updater.stop()' inside a
# handler (shutdown_cmd) causes a deadlock because it waits for itself to finish
def shutdown():
    updater.stop()
    updater.is_idle = False


def start_cmd(updater, bot=None, update=None):
    msg = "TrexTrader is running!\n"
    updater.bot.send_message(
        bot_cfg("TELEGRAM_USER_ID"), msg, reply_markup=keyboard_cmds()
    )


@restrict_access
def shutdown_cmd(bot, update, chat_data):
    update.message.reply_text("Shutting down...", reply_markup=ReplyKeyboardRemove())

    # See comments on the 'shutdown' function
    threading.Thread(target=shutdown).start()


@restrict_access
def restart_cmd(bot, update, chat_data):
    update.message.reply_text(
        "Bot is restarting...", reply_markup=ReplyKeyboardRemove()
    )

    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)
