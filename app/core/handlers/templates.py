from time import strftime, gmtime

from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from app.core.states import States


def search_message_builder(query: str, state: FSMContext, empty: bool):
    if not empty:
        _text = f'Треки по запросу <b>«{query}»</b>:'
    else:
        _text = f'По запросу <b>«{query}»</b> ничего не найдено :('
    if state == States.global_searching.state:
        _text += '\nНе нашли, что искали? Попробуйте локальный поиск – /local'
    else:
        _text += '\nНе нашли, что искали? Попробуйте поиск по музыке ВК – /global'
    return _text


def track_description(track):
    formatted_time = strftime("%M:%S" if track.duration < 3600 else "%H:%M:%S", gmtime(track.duration))
    return emojize(f':musical_note: {track.artist} – {track.title} | {formatted_time} |')


def playlist_description(playlist):
    return emojize(f':musical_notes: {playlist.title}')
