import requests
import telebot
import telebot.types
import sqlite3
import matplotlib.pyplot as plt
from contourpy.util import data

bot = telebot.TeleBot('6733585134:AAHnmPsRMGzaE2-iK7pN-bzLmtSqVVbjnS8')
API = '2cb3317cb03e8959325172ad61e856b3'

name = None
password = None
city = None


@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(50), pass varchar(50), city varchar(50))""")
    connect.commit()
    cursor.close()
    connect.close()

    bot.send_message(message.chat.id, 'Проходит регистрация, ваш ник будет: ')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    cursor.execute("""SELECT COUNT(*) FROM users WHERE name = ?""", (name,))
    count = cursor.fetchone()[0]

    cursor.close()
    connect.close()

    if count > 0:
        bot.send_message(message.chat.id, 'Никнейм занят')
        bot.register_next_step_handler(message, user_name)

        return
    else:
        bot.send_message(message.chat.id, 'Введи своё кодовое слово: ')

    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    global password
    password = message.text.strip()
    bot.send_message(message.chat.id, 'Напишите где вы сейчас: ')
    bot.register_next_step_handler(message,user_city )

def user_city(message):
    global city
    city = message.text.strip()

    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    cursor.execute("""INSERT INTO users (name, pass, city) VALUES (:name, :password, :city)""", {"name": name, "password": password, "city": city})
    connect.commit()
    cursor.close()
    connect.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Вы созданы!', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    info = ' '
    for user in users:
        info += f'Имя: {user[1]}, пароль {user[2]}\n'

    cursor.close()
    connect.close()

    bot.send_message(call.message.chat.id, info)

@bot.message_handler(commands=['Weather'])
def weather(message):
    global city, API
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&cnt=7')
    data = res.json()

    main = data['main']
    temperature = main['temp']
    pressure = main['pressure']
    report = data['weather']

    bot.send_message(message.chat.id,f' {city} Температура: {temperature}, Давление: {pressure}, Погода: {report[0]['description']}'), {"name": name, "city": city}


bot.polling(none_stop=True)

