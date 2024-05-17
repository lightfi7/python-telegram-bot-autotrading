import threading

import pytz
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from modules.database import insert_one, find_one, find_many, delete_one, update_one
from modules.telegram import send_message
from modules.iqoption import buy
scheduler = BackgroundScheduler()


def do_trade(task):
    user_id = task['user_id']
    user = find_one('users', {'id': user_id})
    print(user)
    if user is None:
        print(f'Not found a user: {user_id}')
        return
    if 'account' not in user['config']:
        return send_message({
            'chat_id': user_id,
            'text': f'😶 Not found account.'
        })
    if 'email' not in user['config']['account'] or 'password' not in user['config']['account']:
        return send_message({
            'chat_id': user_id,
            'text': f'😶 Not found account email or password.'
        })

    result, profit = buy(task['symbol'], task['amount'], task['option'], 1,
                         user['config']['account']['email'],
                         user['config']['account']['password'])
    print(result, profit)

    if result is None:
        return send_message({
            'chat_id': user_id,
            'text': f'😶 Trade at {task['time']} unsuccessful...'
        })
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
        send_message({
            'chat_id': user_id,
            'text': f'👎You are {result}, {profit}'
        })
        if task['martin_gale'] == 0:
            update_one('tasks', {'_id': task['_id']}, {
                'time': task['protection1'],
                'martin_gale': 1
            })
        elif task['martin_gale'] == 1:
            update_one('tasks', {'_id': task['_id']}, {
                'time': task['protection2'],
                'martin_gale': 2
            })
        elif task['martin_gale'] == 2:
            delete_one('tasks', {'_id': task['_id']})
        else:
            delete_one('tasks', {'_id': task['_id']})
    elif result == 'win':
        send_message({
            'chat_id': user_id,
            'text': f'👍You are {result}, {profit}'
        })
        delete_one('tasks', {'_id': task['_id']})
    elif result == 'balance_off':
        send_message({
            'chat_id': user_id,
            'text': f'😶 Your account balance is running low.\nPlease top up your account'
        })
    elif result == 'payout_off':
        send_message({
            'chat_id': user_id,
            'text': f'😶 Asset payout is low.\n Please try other assets or later'
        })


def scheduled():
    tasks = find_many('tasks', {})
    for task in tasks:
        utc_offset = task['utc_offset']
        scheduled_time_str = task['time']
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
        elif scheduled_datetime < current_datetime_without_tz-timedelta(minutes=30):
            delete_one('tasks', {'_id': task['_id']})
    pass


def start_scheduler():
    scheduler.add_job(scheduled, 'interval', seconds=1)
    scheduler.start()
