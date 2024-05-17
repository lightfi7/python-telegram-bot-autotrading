import time
import logging
from iqoptionapi.stable_api import IQ_Option


# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
def buy(symbal, option, amount, duration):
    Iq = IQ_Option('Allan.traderksa@gmail.com', '%$iqualab%')
    Iq.connect()

    Iq.change_balance('PRACTICE')
    balance = Iq.get_balance()

    if balance < amount:
        return 'balance', 0

    _, order_id = Iq.buy(amount, symbal, option, duration)
    while Iq.get_async_order(order_id) is None:
        pass
    (result, profit) = Iq.check_win_v4(order_id)
    print(result, profit)
    return result, profit
