from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize


class UserProfileMarkup:
    @staticmethod
    def markup():
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=emojize('Изменить ID:arrows_counterclockwise:'),
                                 callback_data='change'),
            InlineKeyboardButton(text=emojize('Мои аудио:headphones:'),
                                 callback_data='audios'),
            InlineKeyboardButton(text=emojize('Мои плейлисты:minidisc:'),
                                 callback_data='playlists')
        )
