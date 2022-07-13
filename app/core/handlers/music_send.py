from aiogram.types import CallbackQuery

from app.core.handlers.music_search import searcher
from app.core.loader import dp, bot, music
from app.core.markups.inline import SearchResultsMarkup
from app.core.services import manager
from app.core.states import States


@dp.callback_query_handler(
    SearchResultsMarkup.data.filter(action=SearchResultsMarkup.actions.select),
    state=States.searching
)
async def send_track(callback_query: CallbackQuery, callback_data: dict):
    """
    Хендлер отправки выбранного трека.
    :param callback_query: Callback Query
    :param callback_data: Callback Data
    """
    _user_id = callback_query.from_user.id
    track_id = int(callback_data['track_id'])
    track = searcher[_user_id].track(track_id)

    file_id = await manager.get_file_id(track, music, bot)
    await callback_query.message.answer_audio(file_id)
    await callback_query.answer()
