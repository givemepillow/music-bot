from aiogram import types
from aiogram.types import Message
from aiovkmusic.exceptions import NonExistentUser

from app.core.extensions import MessageBox
from app.core.loader import dp
from app.core.markups.inline import UserProfileMarkup
from app.core.services.users import UserStorage
from app.core.states import States


@dp.message_handler(state=States.setting_link, chat_type=[types.ChatType.PRIVATE])
async def set_link(message: Message):
    user_id = message.from_user.id
    link = message.text
    wait_message = await message.answer(text='Идет проверка...')
    MessageBox.put(wait_message, user_id)
    try:
        await UserStorage.put_music(vk_user=link, tg_user_id=user_id)
        _music = await UserStorage.get_music(user_id)
        if not _music.is_public():
            await message.answer(text='Аудиозаписи или страница закрыты! Откройте их для общего доступа и повторите '
                                      'попытку.')
        else:
            await message.answer(text=f'Отлично! Ссылка <b>{link}</b> установлена.', parse_mode='HTML')
            await MessageBox.delete_last(user_id)
            _message = await message.answer(
                text=f'VK ID: <b>{_music.user_id}</b>',
                parse_mode='HTML',
                reply_markup=UserProfileMarkup.markup()
            )
            MessageBox.put(_message, message.from_user.id)
            await States.profile.set()
    except NonExistentUser:
        await message.answer(text='Ссылка имеет неверный формат или страница не найдена!\nПопробуйте еще раз.')
        await MessageBox.delete_last(user_id)
