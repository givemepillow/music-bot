from time import strftime, gmtime

from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize
from aiovkmusic import Playlist, Track

from app.core.states import States


class TextBuilder:
    @staticmethod
    def start(username):
        return \
            f'Привет{f", <b>{username}</b>"}!\n' \
            f'Данный бот умеет искать и загружать музыку из <b>ВК</b>!\n' \
            f'Чтобы найти аудиозапись, отправьте название песни или исполнителя боту.'

    @staticmethod
    def global_search():
        return 'Поиск по <b>ВК</b>...'

    @staticmethod
    def link():
        return 'Введите ссылку на страницу (или ID):'

    @staticmethod
    def profile(username):
        return f'Пользователь VK: <b>{username}</b>'

    @staticmethod
    def empty_link():
        return 'Для доступа к меню профиля установите ссылку на VK: <b>/link</b>'

    @staticmethod
    def local_search():
        return 'Поиск треков по сохраненным в базе данных...'

    @staticmethod
    def playlist_description(playlist: Playlist):
        return emojize(f':musical_notes: {playlist.title}')

    @staticmethod
    def track_description(track: Track):
        formatted_time = strftime("%M:%S" if track.duration < 3600 else "%H:%M:%S", gmtime(track.duration))
        return emojize(f':musical_note: {track.artist} – {track.title} | {formatted_time} |')

    @staticmethod
    def search_results(query: str, state: FSMContext, empty: bool):
        if not empty:
            _text = f'Треки по запросу <b>«{query}»</b>:'
        else:
            _text = f'По запросу <b>«{query}»</b> ничего не найдено :('
        if state == States.global_searching.state:
            _text += '\nНе нашли, что искали? Попробуйте локальный поиск – /local'
        else:
            _text += '\nНе нашли, что искали? Попробуйте поиск по музыке ВК – /global'
        return _text

    @staticmethod
    def closed_audio():
        return 'Аудиозаписи или страница закрыты! Откройте их для общего доступа и повторите попытку.'

    @staticmethod
    def link_updated(link: str):
        return f'Отлично! Ссылка <b>{link}</b> установлена.'

    @staticmethod
    def incorrect_link():
        return 'Ссылка имеет неверный формат или страница не найдена!\nПопробуйте еще раз.'

    @staticmethod
    def wait_for_checking():
        return 'Идет проверка...'
