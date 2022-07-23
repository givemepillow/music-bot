from aiogram import types
from aiogram.types import CallbackQuery

from app.core.handlers.base import registry, crud
from app.core.loader import dp, bot, music
from app.core.markups.inline import ResultsMarkup
from app.core.services import manager
from app.core.states import States


@dp.callback_query_handler(
    ResultsMarkup.data.filter(action=ResultsMarkup.actions.select),
    state=[States.global_searching, States.local_searching, States.playlist_tracks, States.user_tracks],
    chat_type=[types.ChatType.PRIVATE]
)
async def music_sender(callback_query: CallbackQuery, callback_data: dict):
    user_id = callback_query.from_user.id
    await bot.send_chat_action(chat_id=user_id, action='upload_audio')
    track_id = int(callback_data['item_id'])
    try:
        file_id = await manager.get_file_id(registry[user_id].get(track_id), music, bot, crud)
        await callback_query.message.answer_audio(file_id)
    except KeyError:
        await callback_query.answer()
