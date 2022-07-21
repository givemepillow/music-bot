from dataclasses import dataclass
from time import strftime, gmtime

import loguru
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.emoji import emojize
from aiovkmusic import Track

__all__ = ['SearchResultsMarkup']


@dataclass(frozen=True)
class _Actions:
    prev = 'prev'
    next = 'next'
    select = 'select'
    back = 'back'


class _SearchResultsMarkup:

    def __init__(self, tracks: list[Track], count: int, pages: int, callback_data: CallbackData, searcher_generator):
        self._count: int = count
        self._current_page: int = 0
        self._pages: int = pages
        self._tracks: list[Track] = tracks
        self._data = callback_data
        self._searcher_generator = searcher_generator

    def build_markup(self, callback_data, back_button: bool):
        markup = InlineKeyboardMarkup(row_width=2)
        if callback_data is not None:
            match callback_data['action']:
                case _Actions.next:
                    self._next()
                case _Actions.prev:
                    self._prev()
        for track in self._tracks:
            formatted_time = strftime("%M:%S" if track.duration < 3600 else "%H:%M:%S", gmtime(track.duration))
            _text = emojize(f':musical_note: {track.artist} – {track.title} | {formatted_time} |')
            markup.add(InlineKeyboardButton(text=_text, callback_data=self._data.new(_Actions.select, track.id)))
        if not self._tracks:
            return markup
        buttons = []
        if self._current_page > 0:
            buttons.append(
                InlineKeyboardButton(
                    text=emojize(':arrow_left:'),
                    callback_data=self._data.new(_Actions.prev, 0)
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=' ',
                    callback_data='_'
                )
            )

        if self._current_page < self._pages - 1 and len(self._tracks) >= self._count:
            buttons.append(
                InlineKeyboardButton(
                    text=emojize(':arrow_right:'),
                    callback_data=self._data.new(_Actions.next, 0)
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=' ',
                    callback_data='_'
                )
            )
        markup.add(*buttons)
        if back_button:
            markup.add(
                InlineKeyboardButton(
                    text=emojize('Назад :leftwards_arrow_with_hook:'),
                    callback_data=self._data.new(_Actions.back, 0)
                )
            )
        return markup

    def _next(self):
        self._tracks = self._searcher_generator.next()
        if self._current_page != self._pages - 1:
            self._current_page += 1

    def _prev(self):
        self._tracks = self._searcher_generator.prev()
        if self._current_page != 0:
            self._current_page -= 1


class SearchResultsMarkup:
    _storage: dict[int, _SearchResultsMarkup] = dict()
    data = CallbackData('tracks', 'action', 'track_id')
    actions = _Actions()

    @classmethod
    def setup(cls, tracks: list[Track], searcher_generator, user_id: int, count: int = 7, pages: int = 5):
        cls._storage[user_id] = _SearchResultsMarkup(
            tracks=tracks,
            count=count,
            pages=pages,
            callback_data=cls.data,
            searcher_generator=searcher_generator
        )

    @classmethod
    def clear(cls, user_id):
        try:
            del cls._storage[user_id]
        except KeyError as err:
            loguru.logger.warning(str(err))

    @classmethod
    def markup(cls, user_id, back_button: bool = False, callback_data=None):
        return cls._storage[user_id].build_markup(callback_data, back_button)
