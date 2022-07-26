import abc
from typing import Optional

from aiogram import types as tg_types
from aiovkmusic.exceptions import NonExistentUser

from app.core.extensions import MessageBox
from app.core.handlers.base import registry, crud, text_builder
from app.core.loader import bot, music
from app.core.markups.inline import UserProfileMarkup
from app.core.services import manager
from app.core.services.users import UserStorage
from app.core.states import States
from app.utils import Singleton


class Handler(Singleton):
    def __init__(self):
        from_user: Optional[tg_types.User]


class MessageHandler(Handler, abc.ABC):
    async def __call__(self, message: tg_types.Message, *args, **kwargs):
        self.from_user = message.from_user
        await self.handle(message, *args, **kwargs)

    @abc.abstractmethod
    async def handle(self, message: tg_types.Message, *args, **kwargs):
        pass


class CallbackQueryHandler(Handler, abc.ABC):
    async def __call__(self, callback_query: tg_types.CallbackQuery, *args, **kwargs):
        self.from_user = callback_query.from_user
        self.callback_data = kwargs['callback_data']
        await self.handle(callback_query, *args, **kwargs)

    @abc.abstractmethod
    async def handle(self, callback_query: tg_types.CallbackQuery, *args, **kwargs):
        pass


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


class MusicSenderHandler(CallbackQueryHandler):
    async def handle(self, callback_query: tg_types.CallbackQuery, *args, **kwargs):
        await bot.send_chat_action(self.from_user.id, action='upload_audio')
        try:
            track_id = int(self.callback_data['item_id'])
            file_id = await manager.get_file_id(registry[self.from_user.id].get(track_id), music, bot, crud)
            await callback_query.message.answer_audio(file_id)
        except KeyError:
            await callback_query.answer()
