import requests
import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
SOURCE_CHANNEL_ID = os.getenv('SOURCE_CHANNEL_ID', '')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', '')


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


def setup_webhook(url=WEBHOOK_URL):
    try:
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setwebhook?url={url}')
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)
