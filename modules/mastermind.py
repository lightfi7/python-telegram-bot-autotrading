# mastermind.py
import os
import re
from modules.cache import cached, cache
from config import OPTIONS, LANGUAGES
from modules.database import insert_one
from modules.telegram import send_message, copy_message
from modules.utils import generate_key, verify_key, is_hex

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
    pattern = r'(?:🚦ATENÇÃO M5🚦UTC -(\d+)\n\n)?([\w/]+);(\d+:\d+);(\w+)\s🟥\n\n👇🏼Em caso de loss👇🏼\n\n1º Proteção ; (\d+:\d+)\n2º Proteção ; (\d+:\d+)'

    match = re.search(pattern, data)

    if match:
        utc_offset = match.group(1)
        symbol = match.group(2)
        time1 = match.group(3)
        option = match.group(4)
        protection1 = match.group(5)
        protection2 = match.group(6)

        if utc_offset:
            pass
        else:
            utc_offset = 3

        print(f"UTC-{utc_offset}")
        print(f"Symbol: {symbol}")
        print(f"Time: {time1}")
        print(f"Option: {option}")
        print(f"1st Protection: {protection1}")
        print(f"2nd Protection: {protection2}")

        return f'{utc_offset},{symbol},{time1},{option},{protection1},{protection2}'
    else:
        print("No match found.")
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
                'language': 'English 🇺🇸',
                'level': 0,
                'last_action': '',
                'config': {},
                'perm': 'guest',
            })
            if callback_type == '@language':
                user['language'] = callback_data
                user['last_action'] = 'language'
                cached(user_id, user)
                if 'perm' in user and user['perm'] == 'user':
                    msg = (
                        f'🌐 Selected language: {callback_data}\n\n'
                    )
                    json= {
                        'chat_id': user_id,
                        'text': msg
                    }
                    return send_message(json)
                else:
                    json= {
                        'chat_id': user_id,
                        'text': f'🌐 Selected language: {callback_data}\n\n'
                                f'📌 You \'re not currently subscribed.\n\n'
                                f'🎁 Use the /membership command to upgrade your membership.',
                        'parse_mode': 'html'}
                    return send_message(json)
            elif callback_type == '@option':
                if callback_data == 'account':
                    user['last_action'] = 'account'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': 'Real Account' + (
                                ' ✅' if 'config' in user['config'] and user['config']['account'] == 1 else ''),
                              'value': '@real'},
                             {'label': 'Practice Account' + (
                                 ' ✅' if 'config' in user['config'] and user['config']['account'] == 2 else ''),
                              'value': '@practice'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': '‍♂️ Choose account type',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    return send_message(json)
                elif callback_data == 'trading_amount':
                    user['last_action'] = 'trading_amount'
                    json = {
                        'chat_id': user_id,
                        'text': 'Enter trading amount'
                    }
                    return send_message(json)
                elif callback_data == 'strategy':
                    user['last_action'] = 'strategy'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': 'Fix amount', 'value': '@fix_amount'},
                             {'label': '%over the balance', 'value': '@over_balance'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': '💎 Choose strategy',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    return send_message(json)
                elif callback_data == 'martin_gale':
                    user['last_action'] = 'martin_gale'
                    keyboard = [
                        [{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in opts]
                        for opts in [
                            [{'label': 'Up to M.Gale 1' + (
                                ' ✅' if 'config' in user['config'] and user['config']['@up2m.gale'] == 1 else ''),
                              'value': '@up2m.gale1'},
                             {'label': 'Up to M.Gale 2' + (
                                 ' ✅' if 'config' in user['config'] and user['config']['@up2m.gale'] == 2 else ''),
                              'value': '@up2m.gale2'}, ]
                        ]]
                    json = {
                        'chat_id': user_id,
                        'text': '⚖ Choose martin gale',
                        'reply_markup': {
                            'inline_keyboard': keyboard
                        }
                    }
                    return send_message(json)
                elif callback_data == '@real':
                    user['config']['account'] = 1
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'You set Account type as `Real`',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif callback_data == '@practice':
                    user['config']['account'] = 2
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'You set Account type as `Practice`',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif callback_data == '@up2m.gale1':
                    user['config']['@up2m.gale'] = 1
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'You set Martin Gale as `Up to M.Gale 1`',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif callback_data == '@up2m.gale2':
                    user['config']['@up2m.gale'] = 2
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'You set Martin Gale as `Up to M.Gale 2`',
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif callback_data == '@fix_amount':
                    user['last_action'] = 'fix_amount'
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'Enter fix amount',
                    }
                    return send_message(json)
                elif callback_data == '@over_balance':
                    user['last_action'] = 'over_balance'
                    cached(user_id, user)
                    json = {
                        'chat_id': user_id,
                        'text': 'Enter % over the balance',
                    }
                    return send_message(json)
                else:
                    pass
            elif callback_type == '@trade':
                utc_offset, symbol, time1, option, protection1, protection2 = callback_data.split(',')

                # make schedule
                insert_one('tasks', {
                    'user_id': user_id,
                    'utc_offset': utc_offset,
                    'symbol': symbol,
                    'time': time1,
                    'option': option,
                    'protection1': protection1,
                    'protection2': protection2,
                })
                pass
        elif t == 'message':
            user_id = query['from']['id']
            text = query['text']
            user = cached(user_id, {
                'id': query['from']['id'],
                'username': query['from']['username'],
                'language': 'English 🇺🇸',
                'level': 0,
                'last_action': '',
                'config': {},
                'perm': 'guest',
            })
            # Add your logic to generate a response based on the incoming message text
            if '/start' in text.lower():
                if user['perm'] == 'user':
                    msg = '✌️ Your bot was started'
                    json = {
                        'chat_id': user_id,
                        'text': msg,
                    }
                    return send_message(json)
                else:
                    msg = (
                        "✨ Welcome!\n Please select your preferred language:"
                    )
                    keyboard = [[{'text': item, 'callback_data': f'@language>{item}'} for item in group] for group in
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
                    "🌐 Please select your preferred language:"
                )
                keyboard = [[{'text': item, 'callback_data': f'@language>{item}'} for item in group] for group in
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
                        '👌 You \'re all set! \nYour subscription is active and ready for you to start the bot'
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
                    '🙂 Please choose your membership'
                )
                keyboard = [
                    [
                        {
                            'text': '💧 Monthly',
                            'url': f'https://pay.kiwify.com.br/CAUz5sz?btoken={token}&chat_id={user_id}'
                        },
                        {
                            'text': '🔥 Annual',
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
                keyboard = [[{'text': opt['label'], 'callback_data': f'@option>{opt["value"]}'} for opt in group]
                            for group in OPTIONS]
                json = {
                    'chat_id': user_id,
                    'text': '⚙ Setting',
                    'reply_markup': {
                        'inline_keyboard': keyboard
                    }
                }
                return send_message(json)
            else:
                if user['last_action'] == 'trading_amount':
                    user['config']['trading_amount'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': 'Trading amount is set to `{}`'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'fix_amount':
                    user['config']['fix_amount'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': 'Fix amount is set to `{}`'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                elif user['last_action'] == 'over_balance':
                    user['config']['over_balance'] = int(query['text'])
                    cached(user_id, user)
                    user['last_action'] = None
                    json = {
                        'chat_id': user_id,
                        'text': 'Over % balance is set to `{}`'.format(query['text']),
                        'parse_mode': 'markdown'
                    }
                    return send_message(json)
                else:
                    pass
        elif t == 'result':
            user_id = query['from']['id']
            user = cached(user_id,
                          {
                              'id': query['from']['id'],
                              'username': query['from']['username'],
                              'language': 'English 🇺🇸',
                              'level': 0,
                              'last_action': '',
                              'config': {},
                              'perm': 'guest',
                          })
            if user['last_action'] == 'token':
                if user['perm'] == 'quest':
                    json = {
                        'chat_id': user_id,
                        'text': '😁 Start the bot using the /stat command.'
                    }
                    return send_message(json)
                elif user['perm'] != 'user':
                    if is_hex(query['text']) and verify_key(query['from']['id'],
                                                            bytes.fromhex(query['text'])):
                        user['perm'] = 'user'
                        cached(user_id, user)
                        user['last_action'] = None
                        json = {
                            'chat_id': user_id,
                            'text': '😍 Successfully started the bot'
                        }
                        return send_message(json)
                    else:
                        json = {
                            'chat_id': user_id,
                            'text': '🤨 Invalid token. Please try again. If the problem persists, '
                                    'please contact support.'
                        }
                        return send_message(json)
            elif user['last_action'] == 'trading_amount':
                user['config']['trading_amount'] = int(query['text'])
                cached(user_id, user)
                user['last_action'] = None
                json = {
                    'chat_id': user_id,
                    'text': 'Trading amount is set to `{}`'.format(query['text']),
                    'parse_mode': 'markdown'
                }
                return send_message(json)
            elif user['last_action'] == 'fix_amount':
                user['config']['fix_amount'] = int(query['text'])
                cached(user_id, user)
                user['last_action'] = None
                json = {
                    'chat_id': user_id,
                    'text': 'Fix amount is set to `{}`'.format(query['text']),
                    'parse_mode': 'markdown'
                }
                return send_message(json)
            elif user['last_action'] == 'over_balance':
                user['config']['over_balance'] = int(query['text'])
                cached(user_id, user)
                user['last_action'] = None
                json = {
                    'chat_id': user_id,
                    'text': 'Over % balance is set to `{}`'.format(query['text']),
                    'parse_mode': 'markdown'
                }
                return send_message(json)
        elif t == 'channel_post':
            if query['sender_chat']['id'] == int(SOURCE_CHANNEL_ID):
                for uid in cache.keys():
                    if cache[uid]['perm'] == 'guest':
                        continue
                    trade_option = parse_channel_post(query['text'])
                    keyboard = [
                        [{'text': '⚡ Trade',
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
                            'approved_date' : query['approved_date'],
                            'subscription': query['subscription'],

                        }
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'👍 Thank you for your payment!'
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
                            'approved_date' : query['approved_date'],
                            'subscription': query['subscription'],

                        }
                        cached(user['id'], user)
                        query['user'] = user['id']
                        insert_one('invoices', query)
                        json = {
                            'chat_id': user['id'],
                            'text': f'👍 Thank you for your payment!'
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
                            'text': f'😐 Your subscription payment is overdue. \nPlease update your payment method to avoid disruption in service'
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
                            'text': f'😐 Your subscription has been canceled'
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
        print(e);
        json = {
            'chat_id': user_id,
            'text': '😶 An unexpected error occurred. Please contact support.'
        }
        send_message(json)
