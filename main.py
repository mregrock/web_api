import telebot
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

bot = telebot.TeleBot('1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A')

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('/start', '/Search_music')
keyboard1.add('/help', '/close_keyboard')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я Магнитола Бот. Напишите мне номер команды и я их выполню.\n"
                     + "Напиши мне /help для большей информации.",
                     reply_markup=keyboard1)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Номера команд',
                     reply_markup=keyboard1)


@bot.message_handler(commands=['close_keyboard'])
def close_keyboard_message(message):
    bot.send_message(message.chat.id, 'Принял к сведению',
                     reply_markup=keyboard2)


@bot.message_handler(content_types=['text'])
def send_songs(message):
    if message.text == '/Search_music':
        audio = open('123.mp3', 'rb')
        bot.send_chat_action(message.from_user.id, 'upload_audio')
        bot.send_audio(message.from_user.id, audio)
        audio.close()


bot.polling()
