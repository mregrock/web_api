from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler


def start(update, context):
    update.message.reply_text(
        "Привет! Я Магнитола Бот. Напишите мне номер команды и я их выполню.\n"
        + "Напиши мне \\help для большей информации.")


def help(update, context):
    update.message.reply_text(
        "Номера команд")


def music(update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater("1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
