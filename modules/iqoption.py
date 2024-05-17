import time
import logging

from iqoptionapi.stable_api import IQ_Option

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


def buy(symbal, amount, option, duration, email, password, mode = 'PRACTICE'):
    # if email is None or password is None:
    #     email = 'Allan.traderksa@gmail.com'
    #     password = '%$iqualab%'
    print(email, password)
    Iq = IQ_Option(email, password)
    Iq.connect()

    print(Iq.get_all_ACTIVES_OPCODE())

    Iq.change_balance(mode)
    balance = Iq.get_balance()

    payout = Iq.get_digital_payout(symbal)
    print(payout)

    if payout < 30:
        return 'payout_off', 0

    if balance < amount:
        return 'balance_off', 0

    _, id = (Iq.buy_digital_spot(symbal, amount, option, duration))
    if id != "error":
        while True:
            check, win = Iq.check_win_digital_v2(id)
            if check:
                break
        if win < 0:
            print("you loss " + str(win) + "$")
            return 'loss', win
        else:
            print("you win " + str(win) + "$")
            return 'win', win
    else:
        print("please try again")

    return None, None
