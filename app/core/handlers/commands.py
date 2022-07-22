from aiogram import types
from aiogram.types import Message

from app.core.extensions import MessageBox
from app.core.loader import dp
from app.core.markups.inline import UserProfileMarkup
from app.core.services.users import UserStorage
from app.core.states import States


@dp.message_handler(commands='start', state='*', chat_type=[types.ChatType.PRIVATE])
async def start_handler(message: Message):
    username = message.from_user.username
    await message.answer(
        text=f'Привет{f", <b>{username}</b>" if username else ""}!\n'
             f'Данный бот умеет искать и загружать музыку из <b>ВК</b>!\n'
             f'Чтобы найти аудиозапись, отправьте название песни или исполнителя боту.',
        parse_mode='HTML')
    await States.global_searching.set()


@dp.message_handler(commands=['global', 'search'], state='*', chat_type=[types.ChatType.PRIVATE])
async def global_search_commands(message: Message):
    await message.answer(text='Поиск по <b>ВК</b>...', parse_mode='HTML')
    await States.global_searching.set()


@dp.message_handler(commands='link', state='*', chat_type=[types.ChatType.PRIVATE])
async def link_command_handler(message: Message):
    await message.answer(text='Введите ссылку на страницу (или ID):')
    await States.setting_link.set()


@dp.message_handler(commands=['profile', 'id'], state='*', chat_type=[types.ChatType.PRIVATE])
async def profile_command_handler(message: Message):
    _tg_user_id = message.from_user.id
    _music = await UserStorage.get_music(_tg_user_id)
    if _music:
        _message = await message.answer(
            text=f'VK ID: <b>{_music.user_id}</b>',
            parse_mode='HTML',
            reply_markup=UserProfileMarkup.markup()
        )
        MessageBox.put(_message, message.from_user.id)
    else:
        await message.answer(
            text='Для доступа к меню профиля установите ссылку на VK: <b>/link</b>',
            parse_mode='HTML'
        )
    await States.profile.set()


@dp.message_handler(commands='local', state='*', chat_type=[types.ChatType.PRIVATE])
async def local_search_command(message: Message):
    await message.answer(text='Поиск треков по сохраненным в базе данных...')
    await States.local_searching.set()
