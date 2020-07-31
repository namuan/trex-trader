import logging
import logzero
from logzero import logger

formatter = logging.Formatter("%(asctime)-15s: %(message)s")
logzero.formatter(formatter)


class BotLogger:
    @staticmethod
    def info(message):
        logger.info(message)

    @staticmethod
    def error(message):
        logger.error(message)


log = BotLogger()
