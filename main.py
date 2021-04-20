from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import yandex_music

reply_keyboard = [['/start', '/help'],
                  ['/close_keyboard', '/search_track']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
updater = Updater("1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A", use_context=True)
client = yandex_music.Client()

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


def search_track(update, context):
    update.message.reply_text("Введите название песни", reply_markup=markup)
    text_handler = MessageHandler(Filters.text, music)
    dp = updater.dispatcher
    dp.add_handler(text_handler)


def music(update, context):
    name_track = update.message.text
    search_result = client.search(name_track)
    type_ = search_result.best.type
    best = search_result.best.result
    best_result_text = ""
    if type_ in ['track', 'podcast_episode']:
        artists = ''
        if best.artists:
            artists = ' - ' + ', '.join(artist.name for artist in best.artists)
        best_result_text = best.title + artists
    elif type_ == 'artist':
        best_result_text = best.name
    elif type_ in ['album', 'podcast']:
        best_result_text = best.title
    elif type_ == 'playlist':
        best_result_text = best.title
    elif type_ == 'video':
        best_result_text = f'{best.title} {best.text}'
    print(best_result_text)


def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("search_track", search_track))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()