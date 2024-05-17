import os
import requests

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')


def send_message(json_data):
    try:
        print(f'https://api.telegram.org/bot{BOT_TOKEN}/sendmessage')
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendmessage', json=json_data)
        print(response.text)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def copy_message(json_data):
    try:
        print(f'https://api.telegram.org/bot{BOT_TOKEN}/copymessage')
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copymessage', json=json_data)
        print(response.text)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def edit_message(json_data):
    try:
        print(f'https://api.telegram.org/bot{BOT_TOKEN}/editmessagetext')
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editmessagetext', json=json_data)
        print(response.text)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def delete_message(json_data):
    try:
        print(f'https://api.telegram.org/bot{BOT_TOKEN}/deletemessage')
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/deletemessage', json=json_data)
        print(response.text)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def answer_callback_query(json_data):
    try:
        print(f'https://api.telegram.org/bot{BOT_TOKEN}/answercallbackquery')
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/answercallbackquery', json=json_data)
        print(response.text)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def setup_webhook(url=WEBHOOK_URL):
    try:
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setwebhook?url={url}')
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)
