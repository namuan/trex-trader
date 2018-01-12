from enum import Enum, auto


# Enum for workflow handler
class WorkflowEnum(Enum):
    TRADE_CALCULATE_BUY_COST = auto()
    TRADE_CALCULATE_SELL_COST = auto()
    TRADE_SELECT_BUY_ORDER_SIZE = auto()
    TRADE_CHANGE_SELL_PRICE = auto()
    ORDER_CANCEL = auto()
    PRICE_CURRENCY = auto()
    MARKET_INFO = auto()
