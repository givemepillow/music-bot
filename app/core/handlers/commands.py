from aiogram import types
from aiogram.types import Message

from app.core.handlers.templates import show_profile
from app.core.loader import dp
from app.core.services.users import UserStorage
from app.core.states import States


@dp.message_handler(commands='start', state='*', chat_type=[types.ChatType.PRIVATE])
async def start_handler(message: Message):
    """
    Хендлер, обрабатывающий ввод команды /start
    :param message: сообщение пользователя с командой.
    """
    username = message.from_user.username
    await message.answer(
        text=f'Привет{f", <b>{username}</b>" if username else ""}!\n'
             f'Данный бот умеет искать и загружать музыку из <b>ВК</b>!\n'
             f'Чтобы найти аудиозапись, отправьте название песни или исполнителя боту.',
        parse_mode='HTML')
    await States.searching.set()


@dp.message_handler(commands=['global', 'search'], state='*', chat_type=[types.ChatType.PRIVATE])
async def global_search_commands(message: Message):
    """
    Хендлер, обрабатывающий ввод команд /global или /search
    :param message: сообщение пользователя с командой.
    """
    await message.answer(text='Поиск по <b>ВК</b>...', parse_mode='HTML')
    await States.searching.set()


@dp.message_handler(commands='link', state='*', chat_type=[types.ChatType.PRIVATE])
async def link_command_handler(message: Message):
    """
    Хендлер, обрабатывающий ввод команды /link
    :param message: сообщение пользователя с командой.
    """
    await message.answer(text='Введите ссылку на страницу (или ID):')
    await States.setting_link.set()


@dp.message_handler(commands=['profile', 'id'], state='*', chat_type=[types.ChatType.PRIVATE])
async def profile_command_handler(message: Message):
    """
    Хендлер, обрабатывающий ввод команд /profile или /id
    :param message: сообщение пользователя с командой.
    """
    _tg_user_id = message.from_user.id
    _music = await UserStorage.get_music(_tg_user_id)
    if _music:
        _vk_user_id = _music.user_id
        await show_profile(_vk_user_id, message)
        await States.profile.set()
    else:
        await message.answer(
            text='Для доступа к меню профиля установите ссылку на VK: <b>/link</b>',
            parse_mode='HTML'
        )


@dp.message_handler(commands='local', state='*', chat_type=[types.ChatType.PRIVATE])
async def local_search_command(message: Message):
    """
    Хендлер, обрабатывающий ввод команды /local
    :param message: сообщение пользователя с командой.
    """
    await message.answer(text='Поиск треков по сохраненным в базе данных...')
    await States.local_searching.set()
