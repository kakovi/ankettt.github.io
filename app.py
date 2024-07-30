from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '7498464182:AAFLg-D0LSJ-5PVRlD-AfOmQPFZC8GKpOKc'
WEB_APP_URL = 'https://kakovi.github.io/ankettt.github.io/templates/form.html'
TELEGRAM_CHAT_ID = '6656971536'

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        
        if text == '/start':
            send_start_message(chat_id)
    
    return jsonify({"status": "ok"})

def send_start_message(chat_id):
    keyboard = {
        'inline_keyboard': [[{
            'text': 'Заполнить анкету',
            'web_app': {'url': WEB_APP_URL}
        }]]
    }

    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={
            'chat_id': chat_id,
            'text': 'Нажмите кнопку ниже, чтобы заполнить анкету:',
            'reply_markup': json.dumps(keyboard)
        }
    )

    if response.status_code != 200:
        print("Ошибка при отправке сообщения:", response.json())

if __name__ == '__main__':
    app.run(debug=True)
