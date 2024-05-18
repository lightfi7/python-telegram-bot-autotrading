# mastermind.py
import os
import re
from modules.cache import cached, cache
from config import OPTIONS, LANGUAGES
from modules.database import insert_one
from modules.telegram import send_message, copy_message, edit_message, delete_message, answer_callback_query
from modules.utils import generate_key, verify_key, is_hex
from lang import translate

SOURCE_CHANNEL_ID = os.getenv('SOURCE_CHANNEL_ID', '')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', '')


def parse_data(data):
    print(data)
    if 'callback_query' in data:
        return 'callback_query', data['callback_query']
    elif 'result' in data:
        return 'result', data['result']
    elif 'channel_post' in data:
        return 'channel_post', data['channel_post']
    elif 'message' in data:
        return 'message', data['message']
    elif 'webhook_event_type' in data:
        return 'webhook_event_type', data
    return None, data


def parse_channel_post(data):
    pattern = r'(?:🚦ATENÇÃO M5🚦UTC -(\d+)\n\n)?([\w/]+(?:-OTC)?);(\d+:\d+);(\w+)\s🟥\n\n👇🏼Em caso de loss👇🏼\n\n1º Proteção ; (\d+:\d+)\n2º Proteção ; (\d+:\d+)'

    match = re.search(pattern, data)

    if match:
        utc_offset = match.group(1)
        symbol = match.group(2)
        at = match.group(3)
        option = match.group(4)
        protection1 = match.group(5)
        protection2 = match.group(6)

        if utc_offset:
            pass
        else:
            utc_offset = 3
        print(f"UTC-{utc_offset}")
        print(f"Symbol: {symbol}")
        print(f"Time: {at}")
        print(f"Option: {option}")
        print(f"1st Protection: {protection1}")
        print(f"2nd Protection: {protection2}")

        return f'{utc_offset},{symbol},{at},{option},{protection1},{protection2}'
    else:
        print("no match found.")
        return None, None, None, None, None


def generate_response(data):
    user_id = ''
    text = ''
    t, query = parse_data(data)
    print(t, query)
    try:
        if t == 'callback_query':
            [callback_type, callback_data] = query['data'].split('>')
            user_id = query['from']['id']
            user = cached(user_id, {
                'id': query['from']['id'],
                'username': query['from']['username'],
                'language': 'en',
                'level': 0,
                'last_action': '',
                'config': {},
                'perm': 'guest',
            })
            if callback_type == '@language':
                text, user['language'] = f'{callback_data}'.split(':')
                user['last_action'] = 'language'
                cached(user_id, user)
                if 'perm' in user and user['perm'] == 'user':
                    msg = (
                        f'🌐 {translate('selected_language', user['language'])}: {text}\n\n'
                    )
                    json = {
                        'chat_id': user_id,
                        'text': msg
                    }
                    send_message(json)
                else:
                    json = {
                        'chat_id': user_id,
                        'text': f'🌐 {translate('selected_language', user['language'])}: {text}\n\n'
                                f'📌 {translate('no_subscription', user['language'])}',
                        'parse_mode': 'html'}
                    return send_message(json)
            elif callback_type == '@option':
                if callback_data == 'account':
                    user['last_action'] = 'account'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': translate('real_account', user['language']) + (
                                ' ✅' if 'config' in user['config'] and user['config'][''
                                                                                      ''] == 1 else ''),
                              'value': '@real'},
                             {'label': translate('practice_account', user['language']) + (
                                 ' ✅' if 'config' in user['config'] and user['config']['account_type'] == 2 else ''),
                              'value': '@practice'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': f'‍♂️ {translate('choose_account_type', user['language'])}',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    send_message(json)
                if callback_data == 'language':
                    msg = (
                        f"🌐 {translate('choose_account_type', user['language'])}:"
                    )
                    keyboard = [[{'text': item, 'callback_data': f'@language>{item}'} for item in group] for group in
                                LANGUAGES]
                    json = {
                        'chat_id': user_id,
                        'message_id': query['message']['message_id'],
                        'text': msg,
                        'reply_markup': {
                            'inline_keyboard': keyboard,
                            'force_reply': True
                        },
                    }
                    send_message(json)
                elif callback_data == 'trading_amount':
                    user['last_action'] = 'trading_amount'
                    json = {
                        'chat_id': user_id,
                        'text': f'Enter trading amount{translate('', user['language'])}'
                    }
                    send_message(json)
                elif callback_data == 'strategy':
                    user['last_action'] = 'strategy'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': f'{translate('fix_amount', user['language'])}', 'value': '@fix_amount'},
                             {'label': f'{translate('percent_balance', user['language'])}', 'value': '@over_balance'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': f'💎 {translate('choose_strategy', user['language'])}',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    send_message(json)
                elif callback_data == 'martin_gale':
                    user['last_action'] = 'martin_gale'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': f'{translate('martin_gale_1', user['language'])}' + (
                                ' ✅' if 'config' in user['config'] and user['config']['@up2m.gale'] == 1 else ''),
                              'value': '@up2m.gale1'},
                             {'label': f'{translate('martin_gale_2', user['language'])}' + (
                                 ' ✅' if 'config' in user['config'] and user['config']['@up2m.gale'] == 2 else ''),
                              'value': '@up2m.gale2'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': f'⚖ {translate('choose_martin_gale', user['language'])}',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    send_message(json)
                elif callback_data == '@real':
                    user['last_action'] = 'account_email'
                    user['config']['account_type'] = 1
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('set_account_type_real', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    send_message(json)
                elif callback_data == '@practice':
                    user['last_action'] = 'account_email'
                    user['config']['account_type'] = 2
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('set_account_type_practice', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    send_message(json)
                elif callback_data == '@up2m.gale1':
                    user['config']['@up2m.gale'] = 1
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('set_martin_gale_1', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    send_message(json)
                elif callback_data == '@up2m.gale2':
                    user['config']['@up2m.gale'] = 2
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('set_martin_gale_2', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    send_message(json)
                elif callback_data == '@fix_amount':
                    user['last_action'] = 'fix_amount'
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('enter_fix_amount', user['language'])}',
                    }
                    send_message(json)
                elif callback_data == '@over_balance':
                    user['last_action'] = 'over_balance'
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('enter_percent_balance', user['language'])}',
                    }
                    send_message(json)
                else:
                    pass
            elif callback_type == '@trade':
                utc_offset, symbol, at, option, protection1, protection2 = callback_data.split(',')
                amount = 1
                msg = ''
                if 'account' in user['config']:
                    email = user['config']['account']['email']
                    password = user['config']['account']['password']
                    if email is None or password is None:
                        msg = f'{translate('register_email_password', user['language'])}'
                        json = {
                            'chat_id': user_id,
                            'text': msg,
                        }
                        return send_message(json)
                else:
                    msg = f'😯 {translate('account_not_found', user['language'])}'
                    json = {
                        'chat_id': user_id,
                        'text': msg,
                    }
                    return send_message(json)
                if 'trading_amount' in user['config']:
                    amount = user['config']['trading_amount']
                else:
                    amount = 1
                    msg = f'{translate('default_amount', user['language'])}\n'
                insert_one('tasks', {
                    'user_id': user_id,
                    'utc_offset': utc_offset,
                    'symbol': f'{symbol}'.replace('/', ''),
                    'amount': amount,
                    'time': at,
                    'option': option,
                    'protection1': protection1,
                    'protection2': protection2,
                    'martin_gale': 0
                })
                msg += f'😐 {translate('schedule_set', user['language'])}'.format(at, utc_offset)
                json = {
                    'chat_id': user_id,
                    'message_id': query['message']['message_id'],
                    'text': query['message']['text'],
                }
                edit_message(json)
                send_message({
                    'chat_id': user_id,
                    'message_id': query['message']['message_id'],
                    'text': msg
                })
                pass
            else:
                pass
            return answer_callback_query({
                'callback_query_id': query['id'],
                'text': '😊'
            })
        elif t == 'message':
            user_id = query['from']['id']
            text = query['text']
            user = cached(user_id, {
                'id': query['from']['id'],
                'username': query['from']['username'],
                'language': 'en',
                'level': 0,
                'last_action': '',
                'config': {},
                'perm': 'guest',
            })
            # Add your logic to generate a response based on the incoming message text
            if '/start' in text.lower():
                if user['perm'] == 'user':
                    msg = f'✌️ {translate('bot_started', user['language'])}'
                    json = {
                        'chat_id': user_id,
                        'text': msg,
                    }
                    return send_message(json)
                else:
                    msg = (
                        f"✨ {translate('welcome', user['language'])}\n {translate('choose_language', user['language'])}:"
                    )
                    keyboard = [
                        [{'text': item['text'], 'callback_data': f'@language>{item['text']}:{item['lang']}'} for item in
                         group] for group in
                        LANGUAGES]
                    json = {
                        'chat_id': user_id,
                        'text': msg,
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    return send_message(json)
            elif '/language' in text.lower():
                msg = (
                    f"🌐 {translate('choose_language', user['language'])}:"
                )
                keyboard = [
                    [{'text': item['text'], 'callback_data': f'@language>{item['text']}:{item['lang']}'} for item in
                     group] for group in
                    LANGUAGES]
                json = {
                    'chat_id': user_id,
                    'text': msg,
                    'reply_markup': {
                        'inline_keyboard': keyboard
                    }
                }
                return send_message(json)
            elif '/membership' in text.lower():
                if 'perm' in user and user['perm'] == 'user':
                    msg = (
                        f'👌 {translate('welcome_message', user['language'])}'
                    )
                    json = {
                        'chat_id': user_id,
                        'text': msg
                    }
                    return send_message(json)
                token = generate_key(user)
                user['token'] = token
                cached(user_id, user)
                msg = (
                    f'🙂 {translate('choose_membership', user['language'])}'
                )
                keyboard = [
                    [
                        {
                            'text': f'💧 {translate('membership_monthly', user['language'])}',
                            'url': f'https://pay.kiwify.com.br/CAUz5sz?btoken={token}&chat_id={user_id}'
                        },
                        {
                            'text': f'🔥 {translate('membership_annual', user['language'])}',
                            'url': f'https://pay.kiwify.com.br/oJddJmu?btoken={token}&chat_id={user_id}'
                        }
                    ]
                ]
                json = {
                    'chat_id': user_id,
                    'text': msg,
                    'quote': True,
                    'reply_markup': {
                        'inline_keyboard': keyboard
                    }
                }
                return send_message(json)
            elif '/setting' in text.lower():
                keyboard = [
                    [{'text': translate(opt['label'], user['language']), 'callback_data': f'@option>{opt["value"]}'} for
                     opt in group]
                    for group in OPTIONS]
                json = {
                    'chat_id': user_id,
                    'text': '⚙ Setting',
                    'reply_markup': {
                        'inline_keyboard': keyboard
                    }
                }
                return send_message(json)
            elif '/help' in text.lower():
                json = {
                    'chat_id': user_id,
                    'text': 'Developed by ...'
                }
                return send_message(json)
            else:
                if user['last_action'] == 'trading_amount':
                    user['config']['trading_amount'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('trading_amount_set', user['language'])}'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'fix_amount':
                    user['config']['fix_amount'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('fix_amount_set', user['language'])}'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'over_balance':
                    user['config']['over_balance'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': f'{translate('percent_balance_set', user['language'])}'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'account_email':
                    user['last_action'] = 'account_password'
                    if 'account' in user['config']:
                        user['config']['account']['email'] = query['text']
                    else:
                        user['config']['account'] = {
                            'email': query['text'],
                        }
                    cached(user_id, user)
                    delete_message({
                        'chat_id': user_id,
                        'message_id': query['message_id'],
                    })
                    json = {
                        'chat_id': user_id,
                        'text': f'😊 {translate('register_email', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'account_password':
                    user['last_action'] = None
                    if 'account' in user['config']:
                        user['config']['account']['password'] = query['text']
                    else:
                        send_message({
                            'chat_id': user_id,
                            'text': f'😶 {translate('', user['language'])}'
                        })
                    cached(user_id, user)
                    delete_message({
                        'chat_id': user_id,
                        'message_id': query['message_id'],
                    })
                    json = {
                        'chat_id': user_id,
                        'message_id': query['message_id'],
                        'text': f'😊 {translate('account_registered', user['language'])}',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                else:
                    pass
        elif t == 'channel_post':
            if query['sender_chat']['id'] == int(SOURCE_CHANNEL_ID):
                for uid in cache.keys():
                    if cache[uid]['perm'] == 'guest':
                        continue
                    trade_option = parse_channel_post(query['text'])
                    keyboard = [
                        [{'text': f'⚡ Trade{translate('trade', cache[uid]['language'])}',
                          'callback_data': f'@trade>{trade_option}'}]
                    ]
                    json = {
                        'chat_id': uid,
                        'from_chat_id': query['chat']['id'],
                        'message_id': query['message_id'],
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    copy_message(json)
            return
        elif t == 'webhook_event_type':
            webhook_event_type = query['webhook_event_type']

            if webhook_event_type == 'order_approved':
                for user in cache.items():
                    if verify_key(user, query['btoken']):
                        user['perm'] = 'user'
                        user['order'] = {
                            'id': query['order_id'],
                            'status': query['order_status'],
                            'approved_date': query['approved_date'],
                            'subscription': query['subscription'],

                        }
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'👍 {translate('payment_success', user['language'])}'
                        }
                        return send_message(json)
                pass
            elif webhook_event_type == 'order_rejected':

                pass
            elif webhook_event_type == 'order_refunded':

                pass
            elif webhook_event_type == 'subscription_renewed':
                for user in cache.items():
                    if verify_key(user, query['btoken']):
                        user['perm'] = 'user'
                        user['order'] = {
                            'id': query['order_id'],
                            'status': query['order_status'],
                            'approved_date': query['approved_date'],
                            'subscription': query['subscription'],

                        }
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'👍 {translate('payment_success', user['language'])}'
                        }
                        return send_message(json)
                pass
            elif webhook_event_type == 'subscription_late':
                for user in cache.items():
                    if verify_key(user, query['btoken']):
                        user['perm'] = 'quest'
                        user.pop('order')
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'😐 {translate('payment_overdue', user['language'])}'
                        }
                        return send_message(json)
                pass
            elif webhook_event_type == 'subscription_canceled':
                for user in cache.items():
                    if verify_key(user, query['btoken']):
                        user['perm'] = 'quest'
                        user.pop('order')
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'😐 {translate('subscription_canceled', user['language'])}'
                        }
                        return send_message(json)
                pass
            elif webhook_event_type == 'chargeback':

                pass
            elif webhook_event_type == 'pix_created':

                pass
            elif webhook_event_type == 'billet_created':

                pass
            else:
                pass
        else:
            json = {
                'chat_id': user_id,
                'text': '😊'
            }
            send_message(json)
    except Exception as e:
        print('err:', e)
        json = {
            'chat_id': user_id,
            'text': f'😶 {translate('unexpected_error', user['language'])}'
        }
        send_message(json)
