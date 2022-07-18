from aiogram import types
from aiogram.types import Message
from aiovkmusic import Music
from aiovkmusic.exceptions import NonExistentUser

from app.core.extensions import MessageBox
from app.core.loader import dp, session
from app.core.services.users import UserStorage
from app.core.states import States


@dp.message_handler(commands='link', state='*', chat_type=[types.ChatType.PRIVATE])
async def link_command_handler(message: Message):
    await message.answer(text='Введите ссылку на страницу:')
    await States.setting_link.set()


@dp.message_handler(state=States.setting_link, chat_type=[types.ChatType.PRIVATE])
async def set_link(message: Message):
    user_id = message.from_user.id
    link = message.text
    wait_message = await message.answer(text='Идет проверка...')
    MessageBox.put(wait_message, user_id)
    try:
        _music = Music(user=link, session=session)
        if not _music.is_public():
            await message.answer(text='Аудиозаписи или страница закрыты! Откройте их для общего доступа и повторите '
                                      'попытку.')
        else:
            await UserStorage.put_music(vk_user=link, tg_user_id=user_id)
            await message.answer(text=f'Отлично! Ссылка <b>{link}</b> установлена.', parse_mode='HTML')
    except NonExistentUser:
        await message.answer(text='Ссылка имеет неверный формат или страница не найдена!\nПопробуйте еще раз.')
    finally:
        await MessageBox.delete_last(user_id)
