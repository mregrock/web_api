from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaAudio
import yandex_music
import os
import sqlite3

reply_keyboard = [['/start', '/help'],
                  ['/close_keyboard', '/search_track'],
                  ['/add_album', '/give_score']]
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


class GiveScore:
    def __init__(self):
        self.top = list()
        self.text_handler = None
        self.dp = updater.dispatcher

    def find_album(self, update, context):
        self.top = list()
        self.text_handler = None
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        self.user_id = int(update.message.chat_id)
        telegram_ids = cursor.execute("SELECT telegram_id FROM users").fetchall()
        connect.commit()
        if (self.user_id,) not in telegram_ids:
            cursor.execute("INSERT INTO users(telegram_id) VALUES(?)", (self.user_id,))
            connect.commit()
        self.text_handler = MessageHandler(Filters.text, self.search_album)
        self.dp.add_handler(self.text_handler)
        update.message.reply_text("Введите название альбома", reply_markup=markup)

    def search_album(self, update, context):
        self.dp.remove_handler(self.text_handler)
        name_album = update.message.text
        search_result = client.search(name_album)
        text = [f'Результаты по запросу "{name_album}":', '']
        download_file = ""
        best_result_text = ''
        if search_result.best:
            for i in range(min(5, len(search_result.albums.results))):
                type_ = search_result.albums.results[i].type
                best = search_result.albums.results[i]
                artists = ''
                if best.artists:
                    artists = ' - ' + ', '.join(artist.name for artist in best.artists)
                best_result_text = best.title + artists
                download_file = best_result_text + ".jpg"
                self.top.append((download_file, search_result.albums.results[i]))
                text.append(f'{i + 1}. {best_result_text}\n')
        update.message.reply_text('\n'.join(text), reply_markup=markup)
        update.message.reply_text("Введите номер альбома")
        self.text_handler = MessageHandler(Filters.text, self.choose_album)
        self.dp.add_handler(self.text_handler)

    def choose_album(self, update, context):
        try:
            number = int(update.message.text) - 1
            self.top[number][1].download_cover(self.top[number][0])
            text = [self.top[number][0][:-4], '', f"Количество треков: {self.top[number][1].track_count}"]
            update.message.reply_text('\n'.join(text), reply_markup=markup)
            update.message.reply_photo(open(self.top[number][0], 'rb'), reply_markup=markup)
            os.remove(self.top[int(update.message.text) - 1][0])
            self.dp.remove_handler(self.text_handler)
            connect = sqlite3.connect("magnitola_db.db")
            cursor = connect.cursor()
            albums = cursor.execute("SELECT album_yandex_id FROM albums").fetchall()
            connect.commit()
            album = self.top[number][1]
            self.albom_id = album.id
            if (album.id,) not in albums:
                artists = ', '.join(artist.name for artist in album.artists)
                cursor.execute("INSERT INTO albums(album_name, album_artist, album_yandex_id) VALUES(?, ?, ?)",
                               (album.title, artists, album.id))
                connect.commit()
            update.message.reply_text("Введите оценку альбома(от 0 до 10)")
            self.text_handler = MessageHandler(Filters.text, self.give_num_score)
            self.dp.add_handler(self.text_handler)
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")
        except IndexError:
            update.message.reply_text("Ошибка! Введите корректное число")

    def give_num_score(self, update, context):
        number = int(update.message.text)
        if 0 > number > 10:
            number = 5
        self.dp.remove_handler(self.text_handler)
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        connect.commit()
        print(self.albom_id, self.user_id, number)
        cursor.execute("INSERT INTO users_score(album_id, telegram_user_id, score) VALUES(?, ?, ?)",
                       (self.albom_id, self.user_id, number))
        connect.commit()


class AddAlbum:
    def __init__(self):
        self.top = list()
        self.text_handler = None
        self.dp = updater.dispatcher

    def add_album(self, update, context):
        self.top = list()
        self.text_handler = None
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        user_id = int(update.message.chat_id)
        telegram_ids = cursor.execute("SELECT telegram_id FROM users").fetchall()
        connect.commit()
        if (user_id,) not in telegram_ids:
            cursor.execute("INSERT INTO users(telegram_id) VALUES(?)", (user_id,))
            connect.commit()
        self.text_handler = MessageHandler(Filters.text, self.search_album)
        self.dp.add_handler(self.text_handler)
        update.message.reply_text("Введите название альбома", reply_markup=markup)

    def search_album(self, update, context):
        self.dp.remove_handler(self.text_handler)
        name_album = update.message.text
        search_result = client.search(name_album)
        text = [f'Результаты по запросу "{name_album}":', '']
        download_file = ""
        best_result_text = ''
        if search_result.best:
            for i in range(min(5, len(search_result.albums.results))):
                type_ = search_result.albums.results[i].type
                best = search_result.albums.results[i]
                artists = ''
                if best.artists:
                    artists = ' - ' + ', '.join(artist.name for artist in best.artists)
                best_result_text = best.title + artists
                download_file = best_result_text + ".jpg"
                self.top.append((download_file, search_result.albums.results[i]))
                text.append(f'{i + 1}. {best_result_text}\n')
        update.message.reply_text('\n'.join(text), reply_markup=markup)
        update.message.reply_text("Введите номер альбома")
        self.text_handler = MessageHandler(Filters.text, self.choose_album)
        self.dp.add_handler(self.text_handler)

    def choose_album(self, update, context):
        try:
            number = int(update.message.text) - 1
            self.top[number][1].download_cover(self.top[number][0])
            text = [self.top[number][0][:-4], '', f"Количество треков: {self.top[number][1].track_count}"]
            update.message.reply_text('\n'.join(text), reply_markup=markup)
            update.message.reply_photo(open(self.top[number][0], 'rb'), reply_markup=markup)
            os.remove(self.top[int(update.message.text) - 1][0])
            self.dp.remove_handler(self.text_handler)
            connect = sqlite3.connect("magnitola_db.db")
            cursor = connect.cursor()
            albums = cursor.execute("SELECT album_yandex_id FROM albums").fetchall()
            connect.commit()
            album = self.top[number][1]
            if (album.id,) not in albums:
                artists = ', '.join(artist.name for artist in album.artists)
                cursor.execute("INSERT INTO albums(album_name, album_artist, album_yandex_id) VALUES(?, ?, ?)",
                               (album.title, artists, album.id))
                connect.commit()
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")
        except IndexError:
            update.message.reply_text("Ошибка! Введите корректное число")


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
        self.dp.add_handler(self.text_handler)

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
        except IndexError:
            update.message.reply_text("Ошибка! Ввведите корректное число")


def main():
    dp = updater.dispatcher
    music_searcher = MusicSearch()
    adder_album = AddAlbum()
    giver_score = GiveScore()
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("search_track", music_searcher.search_track))
    dp.add_handler(CommandHandler("add_album", adder_album.add_album))
    dp.add_handler(CommandHandler("give_score", giver_score.find_album))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
