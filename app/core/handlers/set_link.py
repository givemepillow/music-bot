from aiogram import types
from aiogram.types import Message

from app.core.loader import dp
from app.core.states import States


@dp.message_handler(commands='link', state='*', chat_type=[types.ChatType.PRIVATE])
async def link_command_handler(message: Message):
    await message.answer(text='Введите ссылку на страницу:')
    await States.setting_link.set()

# @dp.message_handler(state=States.setting_link, chat_type=[types.ChatType.PRIVATE])
# async def set_link(message: Message):
#     link = message.text
#     result = await validate_link(link)
#     if not result:
#         await message.answer(text='Ссылка имеет неверный формат или страница не найдена!\nПопробуйте еще раз.')
#     else:
#         if not music.user_tracks(user_id=link, count=1):
#             await message.answer(text='Аудиозаписи закрыты или их нет! Откройте их для общего доступа и повторите '
#                                       'попытку.')
#         else:
#             await message.answer(text=f'Отлично! Ссылка {link} установлена.')
#         # put link in db
