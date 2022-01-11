import telebot
import config
import random

from random import randint
from telebot import types

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "Команды")
    keyboard.row("/random", "/vk")
    keyboard.row("/weather")
    bot.send_message(message.chat.id, 'Привет! Хочешь узнать свежую информацию о МТУСИ?\n Ты также можешь ознакомиться с другими командами при помощи панели снизу.', reply_markup=keyboard)
    
@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Текущий список команд: /vk ; /random')
    
@bot.message_handler(commands=['vk'])
def vk(message):
    bot.send_message(message.chat.id, 'Ссылка на группу вк: https://vk.com/mtuci/')
 
@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Ознакомиться с прогнозом погоды: https://yandex.ru/pogoda')

@bot.message_handler(commands=['random'])
def random(message):
    bot.send_message(message.chat.id, str(randint(0,100)))
    
@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "хочу":
        bot.send_message(message.chat.id, 'Тогда тебе сюда – https://mtuci.ru/')
    elif  message.text.lower() == "команды":
        bot.send_message(message.chat.id, 'Текущий список команд: /vk ; /random . \n Вы также можете ознакомиться со списком команд через /help ')
    else:
        bot.send_message(message.chat.id, 'Я не понимаю, о чём вы')

bot.polling(none_stop=True)