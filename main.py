from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaAudio
import yandex_music
import os

reply_keyboard = [['/start', '/help'],
                  ['/close_keyboard', '/search_track']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
updater = Updater("1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A", use_context=True)
client = yandex_music.Client.from_credentials('mregrock@yandex.ru', '561867603egorkAgren$5')
top = list()


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
    global top
    download_file = ""
    top = list()
    dp = updater.dispatcher
    dp.remove_handler(MessageHandler(Filters.text, music))
    name_track = update.message.text
    search_result = client.search(name_track)
    text = [f'Результаты по запросу "{name_track}":', '']
    best_result_text = ''
    if search_result.best:
        for i in range(min(5, len(search_result.tracks.results))):
            type_ = search_result.tracks.results[i].type
            best = search_result.tracks.results[i]
            if type_ in ['track', 'podcast_episode', 'music']:
                artists = ''
                if best.artists:
                    artists = ' - ' + ', '.join(artist.name for artist in best.artists)
                best_result_text = best.title + artists
                download_file = best_result_text + ".mp3"
                best.download(download_file)
                top.append(download_file)
            elif type_ == 'artist':
                best_result_text = best.name
            elif type_ in ['album', 'podcast']:
                best_result_text = best.title
            elif type_ == 'playlist':
                best_result_text = best.title
            elif type_ == 'video':
                best_result_text = f'{best.title} {best.text}'

            text.append(f'{i + 1}. {best_result_text}\n')

    if search_result.artists:
        text.append(f'Исполнителей: {search_result.artists.total}')
    if search_result.albums:
        text.append(f'Альбомов: {search_result.albums.total}')
    if search_result.tracks:
        text.append(f'Треков: {search_result.tracks.total}')
    if search_result.playlists:
        text.append(f'Плейлистов: {search_result.playlists.total}')
    if search_result.videos:
        text.append(f'Видео: {search_result.videos.total}')
    text.append('')
    update.message.reply_text('\n'.join(text), reply_markup=markup)


def choose_track(update, context):
    update.message.reply_audio(open(top[int(update.message.text[8:]) - 1], 'rb'), reply_markup=markup)
    os.remove(top[int(update.message.text[8:]) - 1])


def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("search_track", search_track))
    dp.add_handler(CommandHandler("choose", choose_track))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
