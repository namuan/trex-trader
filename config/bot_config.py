import configparser


def config(key, default_value=None):
    c = configparser.ConfigParser()
    c.read("env.cfg")

    return c.get("ALL", key) or default_value


def market_summary_alt_coins():
    all_coins = config("COINS")
    return sorted(all_coins.split(","))
