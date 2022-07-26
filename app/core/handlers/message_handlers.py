from aiogram import types as tg_types
from aiovkmusic.exceptions import NonExistentUser

from app.core.extensions import MessageBox
from app.core.handlers.base import text_builder
from app.core.handlers.handlers import MessageHandler
from app.core.markups.inline import UserProfileMarkup
from app.core.services.users import UserStorage
from app.core.states import States


class StartCommandHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        await message.answer(text_builder.start(self.from_user.first_name), parse_mode='HTML')
        await States.global_searching.set()


class GlobalCommandHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        await message.answer(text_builder.global_search(), parse_mode='HTML')
        await States.global_searching.set()


class LinkCommandHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        await message.answer(text_builder.link())
        await States.setting_link.set()


class LocalCommandHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        await message.answer(text_builder.local_search())
        await States.local_searching.set()


class ProfileCommandHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        _music = await UserStorage.get_music(self.from_user.id)
        if _music:
            _message = await message.answer(
                text_builder.profile(' '.join((_music.first_name, _music.last_name))),
                parse_mode='HTML',
                reply_markup=UserProfileMarkup.markup()
            )
            MessageBox.put(_message, self.from_user.id)
        else:
            await message.answer(text_builder.empty_link(), parse_mode='HTML')
        await States.profile.set()


class UpdateLinkHandler(MessageHandler):
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        link = message.text
        wait_message = await message.answer(text_builder.wait_for_checking())
        MessageBox.put(wait_message, self.from_user.id)
        try:
            await UserStorage.put_music(vk_user=link, tg_user_id=self.from_user.id)
            _music = await UserStorage.get_music(self.from_user.id)
            if not _music.is_public():
                await message.answer(text_builder.closed_audio())
            else:
                await message.answer(text_builder.link_updated(link), parse_mode='HTML')
                await MessageBox.delete_last(self.from_user.id)
                _message = await message.answer(
                    text=text_builder.profile(' '.join((_music.first_name, _music.last_name))),
                    parse_mode='HTML',
                    reply_markup=UserProfileMarkup.markup()
                )
                MessageBox.put(_message, message.from_user.id)
                await States.profile.set()
        except NonExistentUser:
            await message.answer(text_builder.incorrect_link())
            await MessageBox.delete_last(self.from_user.id)
