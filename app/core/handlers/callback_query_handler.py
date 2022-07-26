from aiogram import types as tg_types

from app.core.handlers.base import registry, crud
from app.core.handlers.handlers import CallbackQueryHandler
from app.core.loader import bot, music
from app.core.services import manager


class MusicSenderHandler(CallbackQueryHandler):
    async def handle(self, callback_query: tg_types.CallbackQuery, *args, **kwargs):
        await bot.send_chat_action(self.from_user.id, action='upload_audio')
        try:
            track_id = int(self.callback_data['item_id'])
            file_id = await manager.get_file_id(registry[self.from_user.id].get(track_id), music, bot, crud)
            await callback_query.message.answer_audio(file_id)
        except KeyError:
            await callback_query.answer()
