# mastermind.py
from cache import init_cache, cached
from config import OPTIONS, LANGUAGES


def parse_data(data):
    if 'callback_query' in data:
        return 'callback_query', data['callback_query']
    return 'message', data['message']


def generate_response(data):
    user_id = ''
    text = ''
    t, query = parse_data(data)
    print(t, query)
    if t == 'callback_query':
        [callback_type, callback_data] = query['data'].split('_')
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
                return {
                    'chat_id': user_id,
                    'text': msg
                }

            else:
                return {
                    'chat_id': user_id,
                    'text': f'🌐 Selected language: {callback_data}\n\n'
                            f'📌 Enter your token after upgrade membership to start the bot\n\n'
                            f'🎁 Use the /membership command to upgrade your membership.',
                    'parse_mode': 'html'}
    else:
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
        if '/hello' in text.lower():
            return {
                'chat_id': user_id,
                'text': 'Hello World!'
            }
        elif '/start' in text.lower():
            msg = (
                "✨ Welcome!\n "
                "🌐 Please select your preferred language:"
            )
            keyboard = [[{'text': item, 'callback_data': f'@LANGUAGE_{item}'} for item in group] for group in
                        LANGUAGES]
            return {
                'chat_id': user_id,
                'text': msg,
                'reply_markup': {
                    'inline_keyboard': keyboard
                }
            }
        elif '/membership' in text.lower():
            if 'perm' in user and user['perm'] == 'user':
                msg = (
                    '👌 Your bot was started'
                )

            return {
                'chat_id': user_id,
                'text': ''
            }
            pass
    return {
        'chat_id': user_id,
        'text': '😊'
    }
