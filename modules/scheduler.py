import threading

import pytz
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from modules.database import insert_one, find_many, delete_one, update_one
from modules.iqoption import buy

scheduler = BackgroundScheduler()


def do_trade(task):
    user_id = task['user_id']
    result, profit = buy(task['symbol'], task['option'], task['amount'], 1)

    insert_one('trade_histories', {
        'user_id': user_id,
        'symbol': task['symbol'],
        'option': task['option'],
        'amount': task['amount'],
        'time': task['time'],
        'result': result,
        'profit': profit
    })

    if result == 'loose':
        if task['martin_gale'] == 0:
            update_one('tasks', {'_id': task['_id']}, {'$set': {
                'time': task['protection1'],
                'martin_gale': 1
            }})
        elif task['martin_gale'] == 1:
            update_one('tasks', {'_id': task['_id']}, {'$set': {
                'time': task['protection2'],
                'martin_gale': 2
            }})
        elif task['martin_gale'] == 2:
            delete_one('tasks', {'_id': task['_id']})
    elif result == 'win':
        delete_one('tasks', {'_id': task['_id']})


def scheduled():
    import pytz
    from datetime import datetime, time

    tasks = find_many('tasks', {})
    for task in tasks:
        utc_offset = task['utc_offset']
        symbol = task['symbol']
        amount = task['amount']
        scheduled_time_str = task['time']
        option = task['option']
        protection1 = task['protection1']
        protection2 = task['protection2']
        martin_gale = task['martin_gale']
        if martin_gale == 1:
            scheduled_time_str = protection1
        elif martin_gale == 2:
            scheduled_time_str = protection2

        hour, minute = scheduled_time_str.split(':')
        time_zone = pytz.timezone(f'Etc/GMT+{utc_offset}')

        current_datetime = datetime.now(time_zone)
        scheduled_datetime = datetime.combine(current_datetime.date(),
                                              time(hour=int(hour), minute=int(minute), second=0, microsecond=0),
                                              tzinfo=time_zone)
        current_datetime_without_tz = datetime(current_datetime.year, current_datetime.month, current_datetime.day,
                                               current_datetime.hour, current_datetime.minute, current_datetime.second,
                                               tzinfo=time_zone)

        if scheduled_datetime == current_datetime_without_tz:
            threading.Thread(target=do_trade, args=(task,)).start()
    pass


def start_scheduler():
    scheduler.add_job(scheduled, 'interval', seconds=1)
    scheduler.start()
