# mastermind.py
import os

from cache import cached, cache
from config import OPTIONS, LANGUAGES
from telegram import send_message, copy_message
from utils import generate_key, verify_key, is_hex

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
    return 'etc', data


def generate_response(data):
    user_id = ''
    text = ''
    t, query = parse_data(data)
    print(t, query)
    if t == 'callback_query':
        [callback_type, callback_data] = query['data'].split(':')
        user_id = query['from']['id']
        user = cached(user_id, {
            'id': query['from']['id'],
            'username': query['from']['username'],
            'language': 'English',
            'level': 0,
            'last_action': '',
            'config': {},
            'perm': 'guest',
        })
        if callback_type == '@LANGUAGE':
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
                            f'📌 Enter your token after upgrade membership to start the bot\n\n'
                            f'🎁 Use the /membership command to upgrade your membership.',
                    'parse_mode': 'html'}
                return send_message(json)
        elif callback_type == '@OPTION':
            if callback_data == 'account_type':
                keyboard = [
                    [{'text': opt['label'], 'callback_data': f'@OPTION:{opt["value"]}'} for opt in opts]
                    for opts in [
                        [{'label': 'Real Account' + (
                            ' ✅' if 'config' in user['config'] and user['config']['account_type'] == 1 else ''),
                          'value': '@real'},
                         {'label': 'Practice Account' + (
                             ' ✅' if 'config' in user['config'] and user['config']['account_type'] == 2 else ''),
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
                keyboard = [
                    [{'text': opt['label'], 'callback_data': f'@OPTION:{opt["value"]}'} for opt in opts]
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
                keyboard = [
                    [{'text': opt['label'], 'callback_data': f'@OPTION:{opt["value"]}'} for opt in opts]
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
                user['config']['account_type'] = 1
                cached(user_id, user)
                json = {
                    'chat_id': user_id,
                    'text': 'You set Account type as `Real`',
                    'parse_mode': 'markdown'
                }
                return send_message(json)
            elif callback_data == '@practice':
                user['config']['account_type'] = 2
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
                    'text': 'You set Account type as `Up to M.Gale 1`',
                    'parse_mode': 'markdown'
                }
                return send_message(json)
            elif callback_data == '@up2m.gale2':
                user['config']['@up2m.gale'] = 2
                cached(user_id, user)
                json = {
                    'chat_id': user_id,
                    'text': 'You set Account type as `Up to M.Gale 2`',
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
    elif t == 'message':
        user_id = query['from']['id']
        text = query['text']
        user = cached(user_id, {
            'id': query['from']['id'],
            'username': query['from']['username'],
            'language': 'English',
            'level': 0,
            'last_action': '',
            'config': {},
            'perm': 'guest',
        })
        # Add your logic to generate a response based on the incoming message text
        if '/start' in text.lower():
            msg = (
                "✨ Welcome!\n "
                "🌐 Please select your preferred language:"
            )
            keyboard = [[{'text': item, 'callback_data': f'@LANGUAGE:{item}'} for item in group] for group in
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
                    '👌 Your bot was started'
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
                '🙂 You can upgrade membership by clicking below button'
            )
            keyboard = [
                [
                    {
                        'text': '💧 Monthly',
                        'url': f'https://pay.kiwify.com.br/CAUz5sz?uid={token}&chat_id={user_id}'
                    },
                    {
                        'text': '🔥 Annual',
                        'url': f'https://pay.kiwify.com.br/oJddJmu?uid={token}&chat_id={user_id}'
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
            keyboard = [[{'text': opt['label'], 'callback_data': f'@OPTION:{opt["value"]}'} for opt in group]
                        for group in OPTIONS]
            json = {
                'chat_id': user_id,
                'text': '⚙ Setting',
                'reply_markup': {
                    'inline_keyboard': keyboard
                }
            }
            return send_message(json)
    elif t == 'result':
        user_id = query['from']['id']
        user = cached(user_id,
                      {
                          'id': query['from']['id'],
                          'username': query['from']['username'],
                          'language': 'English',
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
        elif user['last_action'] == 'trading#amount':
            user['config']['trading#amount'] = int(query['text'])
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
                # if cache[uid]['perm'] != 'guest':
                keyboard = [
                    [{'text': '⚡ TRADING',
                      'url': f'https://trade.exnova.com/en/login'}]
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
    json = {
        'chat_id': user_id,
        'text': '😊'
    }
    send_message(json)
