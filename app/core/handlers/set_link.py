from aiogram.types import Message

from app.core.loader import dp
from app.core.states import States
from app.core.tools import validate_link


@dp.message_handler(commands='link')
async def link_command_handler(message: Message):
    await message.answer(text='Введите ссылку на страницу:')
    await States.setting_link.set()


@dp.message_handler(state=States.setting_link)
async def set_link(message: Message):
    link = message.text
    result = await validate_link(link)
    if not result:
        await message.answer(text='Ссылка имеет неверный формат или страница не найдена!\nПопробуйте еще раз.')
    else:
        await message.answer(text=f'Отлично! Ссылка {link} установлена.')
    # put link in db
