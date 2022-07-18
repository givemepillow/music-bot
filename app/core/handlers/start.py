from aiogram import types
from aiogram.types import Message

from app.core.loader import dp
from app.core.states import States


@dp.message_handler(commands='start', state='*', chat_type=[types.ChatType.PRIVATE])
async def start_handler(message: Message):
    username = message.from_user.username
    await message.answer(
        text=f'Привет{f", <b>{username}</b>" if username else ""}!\n'
             f'Данный бот умеет искать и загружать музыку из <b>ВК</b>!\n'
             f'Чтобы найти аудиозапись, отправьте название песни или исполнителя боту.',
        parse_mode='HTML')
    await States.searching.set()


@dp.message_handler(commands=['global', 'search'], state='*', chat_type=[types.ChatType.PRIVATE])
async def global_search_commands(message: Message):
    await message.answer(text='Поиск по <b>ВК</b>...', parse_mode='HTML')
    await States.searching.set()
