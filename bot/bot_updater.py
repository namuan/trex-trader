from telegram.ext import Updater

from config import bot_cfg

# Set bot token, get dispatcher and job queue
bot_token = bot_cfg("TELEGRAM_ORDER_BOT")
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue
