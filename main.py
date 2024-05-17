# app.py
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request
from modules.synctime import sync_utc_time
from modules.cache import init_cache
from modules.telegram import setup_webhook
from modules.mastermind import generate_response
from modules.scheduler import start_scheduler

app = Flask(__name__)


@app.route('/', methods=['POST'])
def handle_update():
    data = request.get_json(force=True)
    generate_response(data)
    return 'OK'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = setup_webhook()
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    init_cache()
    if sync_utc_time() == False:
        start_scheduler()
        app.run(host='0.0.0.0', port=5000)
    else:
        print('UTC time synchronization failed.')
