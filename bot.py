import datetime
import random
import threading

import requests
import telebot
from telebot import types

import config #file with token
import schedule

bot = telebot.TeleBot(config.token, parse_mode=None)
chat_id = 0


def get_day_info(): 
    re = requests.get(
        'https://api.sunrise-sunset.org/json?lat=53.894221&lng=27.482023&date=today&formatted=1').json()
    sr = re['results']['sunrise'].split(':')
    sr[0] = str(int(sr[0]) + 3)
    sunrise = '{}:{}'.format(sr[0], sr[1])
    ss = re['results']['sunset'].split(':')
    ss[0] = str(int(ss[0]) + 15)
    sunset = f'{ss[0]}:{ss[1]}'
    day_lenth = re['results']['day_length']
    text_day = '☀ Время восхода: {} \n 🌇 Время заката: {} \n ⌚ Длительность светового дня: {}'.format(
        sunrise, sunset, day_lenth)
    return text_day


def get_weather():
    re = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?q=Minsk&lang=ru&appid=6fdf3de8bbe6794ac7a7cb712babb4b4&units'
        '=metric').json()
    text_weather = '🌤Погода: {}\n 🌡 Температура: {}°C \n 🥶 Ощущается как: {}°C '.format(
        re['weather'][0]['description'].title(), round(re['main']['temp']), round(re['main']['feels_like']))
    return text_weather


def get_rates():
    re = requests.get('https://developerhub.alfabank.by:8273/partner/1.0.0/public/rates').json()
    text_rates = '💲Курс доллара: \n\t\t 💸 Покупка: {} \n\t\t 🏧 Продажа:{} \n💶Курс евро: \n\t\t 💸 Покупка: {} ' \
                 '\n\t\t 🏧 Продажа:{}' \
                 '\n₽ Курс рубля: \n\t\t 💸 Покупка: {} \n\t\t 🏧 Продажа:{} \n'.format(
        re['rates'][5]['sellRate'], re['rates'][5]['buyRate'], re['rates'][4]['sellRate'], re['rates'][4]['buyRate'],
        re['rates'][3]['sellRate'], re['rates'][3]['buyRate'],
    )
    return text_rates


def get_all():
    disc1 = '\n ---------День--------- \n'
    disc2 = '\n --------Погода-------- \n'
    disc3 = '\n --------Валюты-------- \n'
    date = '📅' + str(datetime.date.today())
    return date + disc1 + get_day_info() + disc2 + get_weather() + disc3 + get_rates()


@bot.message_handler(commands=['start', 'help']) #answer on this commands
def send_welcome(message):
    global chat_id
    chat_id = message.chat.id
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_rates = types.KeyboardButton('Курсы валют') #creation of buttons
    item_weather = types.KeyboardButton('Погода') #creation of buttons
    item_day_info = types.KeyboardButton('День') #creation of buttons 
    item_all = types.KeyboardButton('Все') #creation of buttons
    markup_reply.row(item_rates, item_weather) #put two button in a row
    markup_reply.row(item_day_info, item_all) #put two button in a row
    #     markup_reply.add(item_rates, item_weather, item_day_info, item_all)
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup_reply)

@bot.message_handler(commands=['weather']) #answer on this commands
def send_weather(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, get_weather())


@bot.message_handler(commands=['rates']) #answer on this commands
def send_rates(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, get_rates())


@bot.message_handler(commands=['all']) #answer on this commands
def send_all(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, get_all())


def send_by_schedule():
    disc1 = '\n ---------День--------- \n'
    disc2 = '\n --------Погода-------- \n'
    disc3 = '\n --------Валюты-------- \n'
    date = '📅' + str(datetime.date.today())
    bot.send_message(chat_id, date + disc1 + get_day_info() + disc2 + get_weather() + disc3 + get_rates())


@bot.message_handler(commands=['zhopka'])#answer on this commands
def send_is_zhopka(message):
    global chat_id
    chat_id = message.chat.id
    zhopka = random.randint(1, 10)
    if zhopka % 2 == 0:
        text = 'Денис'
    else:
        text = 'Катя'
    bot.reply_to(message, text)


@bot.message_handler(commands=['sun']) #answer on this commands
def send_sun(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, get_day_info())


def run_bot():
    bot.polling(none_stop=True)


@bot.message_handler(content_types=['text']) 
def handler(message):
    global chat_id
    chat_id = message.chat.id
    if message.text.lower() == 'курсы валют':
        bot.send_message(chat_id, get_rates())
    elif message.text.lower() == 'погода':
        bot.send_message(chat_id, get_weather())
    elif message.text.lower() == 'день':
        bot.send_message(chat_id, get_day_info())
    elif message.text.lower() == 'все':
        bot.send_message(chat_id, get_all())
    else:
        bot.send_message(chat_id, "Попробуйте другую команду, пожалуйста")


schedule.every().day.at("04:00").do(send_by_schedule)
# schedule.every(1).minutes.do(send_sch)

print(chat_id)


def runSchedulers():
    while True:
        schedule.run_pending() #start schedule


if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot) #thread for commands
    t2 = threading.Thread(target=runSchedulers) #thread for scheduler(work not perfect)
    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()
