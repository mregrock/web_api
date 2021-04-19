from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

reply_keyboard = [['/start', '/help'],
                  ['/close_keyboard', '/ ']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(
        "Привет! Я Магнитола Бот. Напишите мне номер команды и я их выполню.\n"
        + "Напиши мне /help для большей информации.",
        reply_markup=markup)


def help(update, context):
    update.message.reply_text(
        "Номера команд",
        reply_markup=markup)


def close_keyboard(update, context):
    update.message.reply_text(
        "Принял к сведению.",
        reply_markup=ReplyKeyboardRemove()
    )


def music(update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater("1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
