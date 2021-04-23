from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaAudio
import yandex_music
import os
import sqlite3
import emoji

reply_keyboard = [['/start', '/help', '/close_keyboard'],
                  ['/search_track'],
                  ['/add_album', '/my_albums']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
updater = Updater("1686818986:AAGY4skTGpvDXKA7iWLgWy3RzpHz5YPAx1A", use_context=True)
client = yandex_music.Client.from_credentials('mregrock@yandex.ru', '561867603egorkAgren$5')
text_handlers = list()


def start(update, context):
    clear_handlers()
    update.message.reply_text(
        "Здравстуй, пользователь! Я никто иной, как Магнитола Бот. Я могу выполнять некоторые, созданные "
        "специально для меня функции. Чтобы подробно разузнать о каждой из них тебе не потребуется много усилий. "
        "Лишь одно волшебное слово: /help. И тогда я выведу тебе всё, что я могу. А сейчас слушай музыку. Приятного "
        "времепровождения.",
        reply_markup=markup)


def help(update, context):
    clear_handlers()
    star = emoji.emojize(':star:')
    update.message.reply_text(
        star + " /start - функция приветствия\n" +
        star + " /help - выводит все функции, которые поддерживает бот\n"+
        star + "/search_track - находит данный пользователем песню, музыку, испольнителя\n" +
        star + "/add_album - даёт способность пользователю оценить альбом для дальнейшего использования\n" +
        star + "/my_albums - выводит всю музыку, которую когда-лиюо оценил пользователь\n",
        reply_markup=markup)


def close_keyboard(update, context):
    clear_handlers()
    update.message.reply_text(
        "Достопочтенный пользователь, я рад сообщить вам, что ваша прихоть была выполнена с превеликим удовольствием. "
        "\nПриятного времепровождения.",
        reply_markup=ReplyKeyboardRemove()
    )


def clear_handlers():
    global text_handlers
    dp = updater.dispatcher
    for i in text_handlers:
        dp.remove_handler(i)


class AddAlbum:
    def __init__(self):
        self.top = list()
        self.text_handler = None
        self.dp = updater.dispatcher
        self.user_id = 0
        self.album_id = 0

    def add_album(self, update, context):
        global text_handlers
        self.top = list()
        self.text_handler = None
        clear_handlers()
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        self.user_id = int(update.message.chat_id)
        telegram_ids = cursor.execute("SELECT telegram_id "
                                      "FROM users").fetchall()
        connect.commit()
        if (self.user_id,) not in telegram_ids:
            cursor.execute("INSERT INTO users(telegram_id) VALUES(?)", (self.user_id,))
            connect.commit()
        print(self.user_id)
        self.text_handler = MessageHandler(Filters.text, self.search_album)
        self.dp.add_handler(self.text_handler)
        text_handlers.append(self.text_handler)
        update.message.reply_text("Введите название альбома", reply_markup=markup)

    def search_album(self, update, context):
        global text_handlers
        self.dp.remove_handler(self.text_handler)
        del text_handlers[text_handlers.index(self.text_handler)]
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
        text_handlers.append(self.text_handler)
        self.dp.add_handler(self.text_handler)

    def choose_album(self, update, context):
        global text_handlers
        try:
            number = int(update.message.text) - 1
            self.top[number][1].download_cover(self.top[number][0])
            text = [self.top[number][0][:-4], '', f"Количество треков: {self.top[number][1].track_count}"]
            update.message.reply_text('\n'.join(text), reply_markup=markup)
            update.message.reply_photo(open(self.top[number][0], 'rb'), reply_markup=markup)
            os.remove(self.top[int(update.message.text) - 1][0])
            del text_handlers[text_handlers.index(self.text_handler)]
            self.dp.remove_handler(self.text_handler)
            connect = sqlite3.connect("magnitola_db.db")
            cursor = connect.cursor()
            albums = cursor.execute("SELECT album_yandex_id "
                                    "FROM albums").fetchall()
            connect.commit()
            album = self.top[number][1]
            self.album_id = album.id
            if (album.id,) not in albums:
                artists = ', '.join(artist.name for artist in album.artists)
                cursor.execute("INSERT INTO albums(album_name, album_artist, album_yandex_id) VALUES(?, ?, ?)",
                               (album.title, artists, album.id))
                connect.commit()
            update.message.reply_text("Введите оценку альбому")
            self.text_handler = MessageHandler(Filters.text, self.give_num_score)
            text_handlers.append(self.text_handler)
            self.dp.add_handler(self.text_handler)
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")
        except IndexError:
            update.message.reply_text("Ошибка! Введите корректное число")

    def give_num_score(self, update, context):
        global text_handlers
        number = int(update.message.text)
        if 0 > number > 10:
            number = 5
        self.dp.remove_handler(self.text_handler)
        del text_handlers[text_handlers.index(self.text_handler)]
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        connect.commit()
        albums_scores = cursor.execute("SELECT album_id, telegram_user_id "
                                       "FROM users_score").fetchall()
        if (self.album_id, self.user_id,) in albums_scores:
            cursor.execute("DELETE FROM users_score "
                           "WHERE album_id == ? AND telegram_user_id == ?",
                           (self.album_id, self.user_id,))
            connect.commit()
        cursor.execute("INSERT INTO users_score(album_id, telegram_user_id, score) VALUES(?, ?, ?)",
                       (self.album_id, self.user_id, number))
        connect.commit()
        update.message.reply_text("Ваша оценка очень важна для нас")


class MusicSearch:
    def __init__(self):
        self.top = list()
        self.text_handler = None
        self.dp = updater.dispatcher

    def search_track(self, update, context):
        global text_handlers
        self.top = list()
        self.text_handler = None
        clear_handlers()
        update.message.reply_text("Введите название песни", reply_markup=markup)
        self.text_handler = MessageHandler(Filters.text, self.music)
        text_handlers.append(self.text_handler)
        self.dp.add_handler(self.text_handler)

    def music(self, update, context):
        global text_handlers
        download_file = ""
        self.dp.remove_handler(self.text_handler)
        del text_handlers[text_handlers.index(self.text_handler)]
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
        text_handlers.append(self.text_handler)
        self.dp.add_handler(self.text_handler)

    def choose_track(self, update, context):
        global text_handlers
        try:
            number = int(update.message.text) - 1
            self.top[number][1].download(self.top[number][0])
            update.message.reply_audio(open(self.top[number][0], 'rb'), reply_markup=markup)
            os.remove(self.top[int(update.message.text) - 1][0])
            del text_handlers[text_handlers.index(self.text_handler)]
            self.dp.remove_handler(self.text_handler)
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")
        except IndexError:
            update.message.reply_text("Ошибка! Ввведите корректное число")


class AlbumPrint:
    def __init__(self, flag=0):
        self.user_id = 0
        self.albums = list()
        self.flag = flag

    def print_album(self, update, context):
        clear_handlers()
        self.user_id = int(update.message.chat_id)
        connect = sqlite3.connect("magnitola_db.db")
        cursor = connect.cursor()
        self.albums = cursor.execute(
            "SELECT albums.album_name, albums.album_artist, users_score.score "
            "FROM users_score INNER JOIN albums ON users_score.album_id == albums.album_yandex_id "
            "WHERE users_score.telegram_user_id == ?", (self.user_id,)).fetchall()
        self.albums.sort(key=lambda x: x[2], reverse=True)
        text = list()
        len_for = len(self.albums)
        if self.flag == 1:
            len_for = 5
        for i in range(len_for):
            text.append(f"{i + 1}. {self.albums[i][0]} - {self.albums[i][1]}")
            text.append(
                f"\n{emoji.emojize(':star:') * self.albums[i][2]} / {emoji.emojize(':star:') * 10} "
                f"({self.albums[i][2]} / 10)\n")
        update.message.reply_text('\n'.join(text))


class Artist:
    def __init__(self):
        self.dp = updater.dispatcher
        self.text_handler = None
        self.top = list()

    def artist_search(self, update, context):
        global text_handlers
        clear_handlers()
        update.message.reply_text("Введите имя артиста")
        self.text_handler = MessageHandler(Filters.text, self.artist_profile)
        text_handlers.append(self.text_handler)
        self.dp.add_handler(self.text_handler)

    def artist_profile(self, update, context):
        global text_handlers
        self.top = list()
        self.dp.remove_handler(self.text_handler)
        del text_handlers[text_handlers.index(self.text_handler)]
        message = update.message.text
        search_result = client.search(message)
        text = list()
        if search_result.artists:
            for i in range(min(5, len(search_result.artists.results))):
                best = search_result.artists.results[i]
                best_result_text = best.name
                download_file = best_result_text + ".jpg"
                self.top.append((download_file, search_result.artists.results[i]))
                text.append(f'{i + 1}. {best_result_text}\n')
        text.append('')
        update.message.reply_text('\n'.join(text), reply_markup=markup)
        update.message.reply_text("Введите номер артиста")
        self.text_handler = MessageHandler(Filters.text, self.choose_artist)
        text_handlers.append(self.text_handler)
        self.dp.add_handler(self.text_handler)

    def choose_artist(self, update, context):
        global text_handlers
        try:
            self.dp.remove_handler(self.text_handler)
            del text_handlers[text_handlers.index(self.text_handler)]
            number = int(update.message.text) - 1
            self.top[number][1].cover.download(self.top[number][0])
            text = list()
            text.append(f"{self.top[number][1].name}")
            update.message.reply_text('\n'.join(text))
            text = list()
            update.message.reply_photo(open(self.top[number][0], 'rb'))
            os.remove(self.top[number][0])
            text.append("Лучшие треки:\n")
            for i in range(min(5, len(self.top[number][1].popular_tracks))):
                best = self.top[number][1].popular_tracks[i]
                artists = ''
                if best.artists:
                    artists = ' - ' + ', '.join(artist.name for artist in best.artists)
                best_result_text = best.title + artists
                text.append(f'{i + 1}. {best_result_text}\n')
            update.message.reply_text('\n'.join(text))
        except ValueError:
            update.message.reply_text("Ошибка! Введите число")
        except IndexError:
            update.message.reply_text("Ошибка! Ввведите корректное число")


def main():
    dp = updater.dispatcher
    music_searcher = MusicSearch()
    adder_album = AddAlbum()
    album_printer = AlbumPrint()
    artist_searcher = Artist()
    top_album_printer = AlbumPrint(flag=1)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("search_track", music_searcher.search_track))
    dp.add_handler(CommandHandler("add_album", adder_album.add_album))
    dp.add_handler(CommandHandler("my_albums", album_printer.print_album))
    dp.add_handler(CommandHandler("my_best_albums", top_album_printer.print_album))
    dp.add_handler(CommandHandler("search_artist", artist_searcher.artist_search))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
