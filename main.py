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


class MusicSearch:
    def __init__(self):
        self.top = list()
        self.text_handler = None
        self.dp = updater.dispatcher

    def search_track(self, update, context):
        self.top = list()
        self.text_handler = None
        update.message.reply_text("Введите название песни", reply_markup=markup)
        self.text_handler = MessageHandler(Filters.text, self.music)
        dp = updater.dispatcher
        dp.add_handler(self.text_handler)

    def music(self, update, context):
        download_file = ""
        self.dp.remove_handler(self.text_handler)
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
                    self.top.append((download_file, search_result.tracks.results[i]))
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
        update.message.reply_text("Введите номер трека")
        self.text_handler = MessageHandler(Filters.text, self.choose_track)
        self.dp.add_handler(self.text_handler)

    def choose_track(self, update, context):
        try:
            number = int(update.message.text) - 1
            self.top[number][1].download(self.top[number][0])
            update.message.reply_audio(open(self.top[number][0], 'rb'), reply_markup=markup)
            os.remove(self.top[int(update.message.text) - 1][0])
            self.dp.remove_handler(self.text_handler)
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")


def main():
    dp = updater.dispatcher
    music_searcher = MusicSearch()
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("search_track", music_searcher.search_track))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
