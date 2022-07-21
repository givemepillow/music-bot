from dataclasses import dataclass

import loguru
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.emoji import emojize
from aiovkmusic import Playlist

from app.core.services.playlists import UserPlaylists

__all__ = ['PlaylistsMarkup']


@dataclass(frozen=True)
class _Actions:
    prev = 'prev'
    next = 'next'
    select = 'select'


class _PlaylistsMarkup:
    def __init__(self, playlists: UserPlaylists, count: int, callback_data: CallbackData):
        self._count: int = count
        self._end: int = count
        self._start: int = 0
        self._playlists: list[Playlist] = playlists.get_playlists()
        self._data = callback_data

    def build_markup(self, callback_data):
        markup = InlineKeyboardMarkup(row_width=2)
        if callback_data is not None:
            match callback_data['action']:
                case _Actions.next:
                    self._next()
                case _Actions.prev:
                    self._prev()
        for playlist in self._playlists[self._start:self._end]:
            _text = emojize(f':musical_notes: {playlist.title}')
            markup.add(InlineKeyboardButton(text=_text, callback_data=self._data.new(_Actions.select, playlist.id)))
        if len(self._playlists) > self._count:
            markup.add(
                InlineKeyboardButton(
                    text=emojize(':arrow_left:'),
                    callback_data=self._data.new(_Actions.prev, 0)
                ),
                InlineKeyboardButton(
                    text=emojize(':arrow_right:'),
                    callback_data=self._data.new(_Actions.next, 0)
                )
            )
        message = f'Плейлисты <b>{self._start + 1}-' \
                  f'{self._end if self._end != len(self._playlists) + 2 else len(self._playlists)}</b> ' \
                  f'из <b>{len(self._playlists)}</b>:'
        return markup, message

    def _next(self):
        if self._start >= len(self._playlists) - self._count:
            self._end = self._count
            self._start = 0
        else:
            self._start += self._count
            self._end += self._count

    def _prev(self):
        if self._start == 0:
            _start = (len(self._playlists) // self._count) * self._count
            self._start = _start if _start != len(self._playlists) else _start - self._count
            self._end = self._start + self._count
        else:
            self._start -= self._count
            self._end -= self._count


class PlaylistsMarkup:
    _storage: dict[int, _PlaylistsMarkup] = dict()
    data = CallbackData('playlists', 'action', 'playlist_id')
    actions = _Actions()

    @classmethod
    def setup(cls, playlists: UserPlaylists, user_id: int, count: int = 5):
        cls._storage[user_id] = _PlaylistsMarkup(
            playlists=playlists,
            count=count,
            callback_data=cls.data
        )

    @classmethod
    def clear(cls, user_id):
        try:
            del cls._storage[user_id]
        except KeyError as err:
            loguru.logger.warning(str(err))

    @classmethod
    def markup(cls, user_id, callback_data=None):
        return cls._storage[user_id].build_markup(callback_data)
