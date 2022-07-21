"""
Модуль с функциями-шаблонами, которые используются в нескольких хендлерах
"""
from aiogram.types import Message

from app.core.handlers.base import playlists
from app.core.loader import bot
from app.core.markups.inline import UserProfileMarkup, PlaylistsMarkup
from app.core.states import States


async def show_profile(vk_user_id: int, message: Message):
    """
    Функция для отображения профиля пользователя.
    :param vk_user_id: ID пользователя в VK.
    :param message: сообщение пользователя.
    """
    await message.answer(
        text=f'VK ID: <b>{vk_user_id}</b>',
        parse_mode='HTML',
        reply_markup=UserProfileMarkup.markup()
    )


async def show_playlists(tg_user_id: int):
    """
    Функция для отображения плейлистов пользователя.
    :param tg_user_id: ID пользователя в Telegram.
    """
    PlaylistsMarkup.setup(
        playlists=await playlists(tg_user_id),
        user_id=tg_user_id,
        count=7
    )

    markup, text = PlaylistsMarkup.markup(user_id=tg_user_id)

    await bot.send_message(
        chat_id=tg_user_id,
        text=text,
        reply_markup=markup,
        parse_mode='HTML'
    )
    await bot.send_message(
        chat_id=tg_user_id,
        text='Чтобы вернуться к поиску, используйте следующие команды:\n'
             '  <b>• /global</b> – для поиска по ВК\n'
             '  <b>• /local</b> – для поиска по базе данных\n',
        parse_mode='HTML'
    )
    await States.playlists.set()
