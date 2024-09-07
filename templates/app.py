from flask import Flask, request, jsonify, redirect
import requests
import gspread
from google.oauth2 import service_account
import os
import logging
import json
from urllib.parse import urlencode

app = Flask(__name__)

# Логирование
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('7498464182:AAFLg-D0LSJ-5PVRlD-AfOmQPFZC8GKpOKc')
MANAGER_CHAT_ID = os.getenv('-4568620668')
SPREADSHEET_URL = os.getenv('https://docs.google.com/spreadsheets/d/1gv_CBblTjobMk2xR_1S0b61dsezAXjUqPKe82Pde0jI/edit?gid=0#gid=0')

# Загрузка учетных данных для Google Sheets из переменной окружения
keyfile_dict = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
creds = service_account.Credentials.from_service_account_info(keyfile_dict)
file = gspread.authorize(creds)
workbook = file.open("New_ankets")
sheet = workbook.sheet1

@app.route('/')
def index():
    return redirect("https://kakovi.github.io/ankettt.github.io/templates/start.html")

@app.route('/form_cash.html')
def form_cash():
    return redirect("https://kakovi.github.io/ankettt.github.io/templates")

@app.route('/form_online.html')
def form_online():
    return redirect("https://kakovi.github.io/ankettt.github.io/templates")

def check_duplicates(accounts, cards):
    """
    Проверка на наличие дубликатов карт и счетов в Google Sheets
    """
    # Получаем все строки из Google Sheets для столбцов A и E
    all_values_a = sheet.col_values(1)  # Столбец A для анкет КЭШ
    all_values_e = sheet.col_values(5)  # Столбец E для анкет Онлайн
    all_values = all_values_a + all_values_e  # Объединяем значения для проверки

    for row in all_values:
        for account in accounts:
            if account in row:
                raise ValueError("Эти реквизиты уже были использованы ранее.")
        for card in cards:
            if card in row:
                raise ValueError("Эти реквизиты уже были использованы ранее.")

@app.route('/submit_cash', methods=['POST'])
def submit_cash():
    try:
        data = request.form.to_dict(flat=False)
        chat_id = data.get('chat_id', [None])[0]

        # Сбор всех номеров карт и счетов из формы
        accounts = {data[f'banks[{i}][account]'][0] for i in range(len([key for key in data.keys() if 'banks[' in key and '][bank]' in key]))}
        cards = set()
        for i in range(len(accounts)):
            cards.update({data[f'banks[{i}][cards][{j}]'][0] for j in range(len([key for key in data.keys() if f'banks[{i}][cards]' in key]))})

        # Проверка на дублирование в обеих анкетах
        check_duplicates(accounts, cards)

        # Формирование данных для записи в Google Sheets
        form_data = (
            f"Анкета на подключение\n"
            f"Агент: @yan_pay\n"
            f"Админ в чате: @helper_kong\n\n"
            f"1. № Чата: {data['chat_number'][0]}\n"
            f"2. ID: {data['id'][0]}\n"
            f"3. ФИО: {data['name'][0]}\n"
            f"4. Владелец ID: @helper_kong\n"
            f"5. IMEI: {data['imei'][0]}\n"
            f"6. Телефон: {data['phone'][0]}\n"
            f"7. Лимит доверия, руб: {data['trust_limit'][0]}\n"
            f"8. Комментарии: {data['comments'][0]}\n"
        )

        if 'add_to_chat' in data and data['add_to_chat'][0].strip() != "":
            form_data += f"Добавить в чат: {data['add_to_chat'][0]}\n"

        for i in range(len(accounts)):
            form_data += f"\n🏦{i+1}\nБанк: {data[f'banks[{i}][bank]'][0]}\n"
            form_data += f"Счет: {data[f'banks[{i}][account]'][0]}\n"
            form_data += f"БИК: {data[f'banks[{i}][bik]'][0]}\n\n"

            for j in range(len([key for key in data.keys() if f'banks[{i}][cards]' in key])):
                form_data += f"💳Карта {j+1}: {data[f'banks[{i}][cards][{j}]'][0]}\n"

        first_empty_row = len(sheet.col_values(1)) + 1
        sheet.update_cell(first_empty_row, 1, form_data)  # Записываем данные в столбец A

        notify_manager(first_empty_row)

        if chat_id:
            send_confirmation(chat_id, form_data)

        logging.info("Анкета КЭШ успешно отправлена и записана в Google Sheets.")

        return redirect("https://kakovi.github.io/ankettt.github.io/templates/submitted.html")

    except ValueError as ve:
        logging.error(f"Ошибка валидации данных: {ve}")
        return redirect(f"https://kakovi.github.io/ankettt.github.io/templates/error.html?{urlencode({'error': str(ve)})}")

    except Exception as e:
        logging.error(f"Ошибка при обработке формы: {e}")
        return redirect(f"https://kakovi.github.io/ankettt.github.io/templates/error.html?{urlencode({'error': 'Произошла ошибка при обработке вашей анкеты. Пожалуйста, попробуйте снова позже.'})}")

@app.route('/submit_online', methods=['POST'])
def submit_online():
    try:
        data = request.form.to_dict(flat=False)
        chat_id = data.get('chat_id', [None])[0]

        # Сбор всех номеров карт и счетов из формы
        accounts = {data[f'banks[{i}][account]'][0] for i in range(len([key for key in data.keys() if 'banks[' in key and '][bank]' in key]))}
        cards = set()
        for i in range(len(accounts)):
            cards.update({data[f'banks[{i}][cards][{j}]'][0] for j in range(len([key for key in data.keys() if f'banks[{i}][cards]' in key]))})

        # Проверка на дублирование в обеих анкетах
        check_duplicates(accounts, cards)

        # Формирование данных для записи в Google Sheets
        form_data = (
            f"Анкета на подключение\n"
            f"Агент: @yan_pay\n"
            f"Админ в чате: {data['owner_id'][0]}\n"
            f"1. № Чата: {data['chat_number'][0]}\n"
            f"2. ID: {data['id'][0]}\n"
            f"3. ФИО: {data['name'][0]}\n"
            f"4. Владелец ID: {data['owner_id'][0]}\n"
            f"5. IMEI: {data['imei'][0]}\n"
            f"6. Телефон: {data['phone'][0]}\n"
            f"7. Лимит доверия, руб: {data['trust_limit'][0]}\n"
            f"8. Комментарии: {data['comments'][0]}\n"
            f"Депозит:\n"
        )

        if 'add_to_chat' in data and data['add_to_chat'][0].strip() != "":
            form_data += f"Добавить в чат: {data['add_to_chat'][0]}\n"

        for i in range(len(accounts)):
            form_data += f"\n🏦{i+1}\nБанк: {data[f'banks[{i}][bank]'][0]}\n"
            form_data += f"Счет: {data[f'banks[{i}][account]'][0]}\n"
            form_data += f"БИК: {data[f'banks[{i}][bik]'][0]}\n\n"

            for j in range(len([key for key in data.keys() if f'banks[{i}][cards]' in key])):
                form_data += f"💳Карта {j+1}: {data[f'banks[{i}][cards][{j}]'][0]}\n"

        first_empty_row = len(sheet.col_values(5)) + 1
        sheet.update_cell(first_empty_row, 5, form_data)  # Записываем данные в столбец E

        notify_manager(first_empty_row, is_online=True)

        if chat_id:
            send_confirmation(chat_id, form_data)

        logging.info("Анкета Онлайн успешно отправлена и записана в Google Sheets.")

        return redirect("https://kakovi.github.io/ankettt.github.io/templates/submitted.html")

    except ValueError as ve:
        logging.error(f"Ошибка валидации данных: {ve}")
        return redirect(f"https://kakovi.github.io/ankettt.github.io/templates/error.html?{urlencode({'error': str(ve)})}")

    except Exception as e:
        logging.error(f"Ошибка при обработке формы: {e}")
        return redirect(f"https://kakovi.github.io/ankettt.github.io/templates/error.html?{urlencode({'error': 'Произошла ошибка при обработке вашей анкеты. Пожалуйста, попробуйте снова позже.'})}")

def send_confirmation(chat_id, form_data):
    message = f"Ваша анкета была успешно подана:\n\n{form_data}"
    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={
            'chat_id': chat_id,
            'text': message
        }
    )

    if response.status_code != 200:
        logging.error(f"Ошибка при отправке сообщения пользователю с chat_id {chat_id}: {response.json()}")
    else:
        logging.info(f"Сообщение успешно отправлено пользователю с chat_id: {chat_id}")

def notify_manager(row_number, is_online=False):
    column_letter = "E" if is_online else "A"  # Используем столбец E для анкет "Онлайн", A для "Под КЭШ"
    cell_link = f"{SPREADSHEET_URL}&range={column_letter}{row_number}"
    message = f"Поступила новая анкета. Проверьте её в Google Таблице:\n{cell_link}"
    
    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={
            'chat_id': MANAGER_CHAT_ID,
            'text': message
        }
    )

    if response.status_code != 200:
        logging.error(f"Ошибка при отправке сообщения менеджеру: {response.json()}")
    else:
        logging.info("Сообщение успешно отправлено менеджеру.")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        
        if text == '/start':
            keyboard = {
                'inline_keyboard': [[{
                    'text': 'Заполнить анкету',
                    'web_app': {'url': f'https://kakovi.github.io/ankettt.github.io/templates/start.html'}
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
                logging.error(f"Ошибка при отправке сообщения: {response.json()}")
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
