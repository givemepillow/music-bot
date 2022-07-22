from aiogram import types
from aiogram.types import CallbackQuery, Message

from app.core.loader import dp


@dp.message_handler(chat_type=[types.ChatType.PRIVATE])
async def start_handler(message: Message):
    await message.answer(
        text='Ничего не понятно – может быть вы хотели найти какую-нибудь аудиозапись <b>/start</b>?',
        parse_mode='HTML'
    )


@dp.callback_query_handler(text=['_'], state='*')
async def plug(callback_query: CallbackQuery):
    await callback_query.answer()
