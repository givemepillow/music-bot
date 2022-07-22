from dataclasses import dataclass
from typing import Callable

import loguru
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.emoji import emojize

__all__ = ['ResultsMarkup']

from app.core.services import Viewer


@dataclass(frozen=True)
class _Actions:
    prev = 'prev'
    next = 'next'
    select = 'select'
    back = 'back'


class _ResultsMarkup:

    def __init__(self, step: int, pages: int, callback_data: CallbackData, viewer: Viewer, description: Callable):
        self._count: int = step
        self._current_page: int = 0
        self._pages: int = pages
        self._items = viewer.next()
        self._data = callback_data
        self._generator = viewer
        self._description = description

    def build_markup(self, callback_data, back_button: bool):
        markup = InlineKeyboardMarkup(row_width=2)
        if callback_data is not None:
            match callback_data['action']:
                case _Actions.next:
                    self._next()
                case _Actions.prev:
                    self._prev()
        for item in self._items:
            markup.add(InlineKeyboardButton(text=self._description(item),
                                            callback_data=self._data.new(_Actions.select, item.id)))
        if not self._items:
            if self._current_page == 0:
                return markup
            markup.add(InlineKeyboardButton(text='А всё, больше ничего нет...', callback_data='_'))
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

        if self._current_page < self._pages - 1 and len(self._items) >= self._count:
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
        self._items = self._generator.next()
        if self._current_page != self._pages - 1:
            self._current_page += 1

    def _prev(self):
        self._items = self._generator.prev()
        if self._current_page != 0:
            self._current_page -= 1


class ResultsMarkup:
    _storage: dict[int, _ResultsMarkup] = dict()
    data = CallbackData('tracks', 'action', 'item_id')
    actions = _Actions()

    @classmethod
    def setup(cls, viewer: Viewer, user_id: int, description: Callable):
        cls._storage[user_id] = _ResultsMarkup(
            step=viewer.step,
            pages=viewer.pages,
            callback_data=cls.data,
            viewer=viewer,
            description=description
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
