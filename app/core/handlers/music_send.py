from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.core.handlers.base import searcher, local_searcher
from app.core.loader import dp, bot, music
from app.core.markups.inline import SearchResultsMarkup
from app.core.services import manager, MusicSearcher
from app.core.services.users import UserStorage
from app.core.states import States


@dp.callback_query_handler(
    SearchResultsMarkup.data.filter(action=SearchResultsMarkup.actions.select),
    state=[States.searching, States.local_searching, States.user_audios, States.playlist_tracks],
    chat_type=[types.ChatType.PRIVATE]
)
async def send_track(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Хендлер отправки выбранного трека.
    :param state: текущее состояние бота.
    :param callback_query: Callback Query
    :param callback_data: Callback Data
    """
    _user_id = callback_query.from_user.id
    await bot.send_chat_action(chat_id=_user_id, action='upload_audio')
    track_id = int(callback_data['track_id'])
    current_state = await state.get_state()
    track = None
    if current_state == 'States:searching':
        track = searcher[_user_id].track(track_id)
    elif current_state == 'States:local_searching':
        track = local_searcher[_user_id].track(track_id)
    elif current_state == 'States:user_audios':
        _music = await UserStorage.get_music(_user_id)
        user_tracks_searcher = MusicSearcher(_music, 1, 1, user_tracks=True)
        track = user_tracks_searcher[_user_id].track(track_id)
    elif current_state == 'States:playlist_tracks':
        _music = await UserStorage.get_music(_user_id)
        playlist_tracks_searcher = MusicSearcher(_music, 7, 10, playlist_tracks=True)
        track = playlist_tracks_searcher[_user_id].track(track_id)
    file_id = await manager.get_file_id(track, music, bot)
    await callback_query.message.answer_audio(file_id)
    # await callback_query.answer()
