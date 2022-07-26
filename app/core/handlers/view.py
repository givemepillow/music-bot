from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from app.core.extensions import MessageBox
from app.core.handlers.base import viewers, registry, searchers, text_builder
from app.core.loader import dp
from app.core.markups.inline import *
from app.core.services.users import UserStorage
from app.core.states import States


@dp.message_handler(
    state=[States.global_searching, States.local_searching],
    chat_type=[types.ChatType.PRIVATE]
)
async def view(message: Message, state: FSMContext):
    _user_id = message.from_user.id
    await MessageBox.delete_last(_user_id)
    current_state = await state.get_state()
    viewer = await searchers[current_state](message.text)
    registry[_user_id] = viewer
    ResultsMarkup.setup(viewer=viewer, user_id=_user_id, description=text_builder.track_description)
    _message = await message.answer(
        text=text_builder.search_results(message.text, current_state, viewer.empty()),
        reply_markup=ResultsMarkup.markup(_user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, _user_id)


@dp.callback_query_handler(
    ResultsMarkup.data.filter(action=[ResultsMarkup.actions.back]),
    state=[States.playlist_tracks],
    chat_type=[types.ChatType.PRIVATE]
)
@dp.callback_query_handler(text='playlists', state=[States.profile], chat_type=[types.ChatType.PRIVATE])
async def playlists(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await MessageBox.delete_last(user_id)
    user_music = await UserStorage.get_music(user_id)
    viewer = await viewers['user_playlists'](user_music)
    registry[user_id] = viewer
    ResultsMarkup.setup(viewer=viewer, user_id=user_id, description=text_builder.playlist_description)
    _message = await callback_query.message.answer(
        text='<b>Плейлисты:</b>',
        reply_markup=ResultsMarkup.markup(user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, user_id)
    await States.playlists.set()


@dp.callback_query_handler(text='audios', state=[States.profile], chat_type=[types.ChatType.PRIVATE])
async def user_tracks(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await MessageBox.delete_last(user_id)
    music = await UserStorage.get_music(user_id)
    viewer = await viewers['user_music'](music)
    registry[user_id] = viewer
    ResultsMarkup.setup(viewer=viewer, user_id=user_id, description=text_builder.track_description)
    _message = await callback_query.message.answer(
        text='Аудиозаписей нет :(' if viewer.empty() else 'Ваши <b>аудиозаписи</b>:',
        reply_markup=ResultsMarkup.markup(user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, user_id)
    await States.user_tracks.set()


@dp.callback_query_handler(text='change', state=[States.profile], chat_type=[types.ChatType.PRIVATE])
async def update_link(callback_query: CallbackQuery):
    await callback_query.message.answer(text='Введите ссылку на страницу (или ID):')
    await States.setting_link.set()


@dp.callback_query_handler(
    ResultsMarkup.data.filter(action=ResultsMarkup.actions.select),
    state=States.playlists,
    chat_type=[types.ChatType.PRIVATE]
)
async def playlist_tracks(callback_query: CallbackQuery, callback_data: dict):
    _user_id = callback_query.from_user.id
    await MessageBox.delete_last(_user_id)
    _music = await UserStorage.get_music(user_id=_user_id)
    playlist_id = int(callback_data['item_id'])
    playlist = registry[_user_id].get(playlist_id)
    viewer = await viewers['playlist_music'](playlist)
    registry[_user_id] = viewer
    ResultsMarkup.setup(viewer=viewer, user_id=_user_id, description=text_builder.track_description)
    _text = ''
    if not viewer.empty():
        _text = f'Треки из плейлиста <b>«{playlist.title}»</b>:'
    else:
        _text = f'В плейлисте <b>«{playlist.title}»</b> нет треков :('
    _message = await callback_query.message.answer(
        text=_text,
        reply_markup=ResultsMarkup.markup(_user_id, back_button=True),
        parse_mode="HTML"
    )
    MessageBox.put(_message, _user_id)
    await States.playlist_tracks.set()


@dp.callback_query_handler(
    ResultsMarkup.data.filter(action=[
        ResultsMarkup.actions.next, ResultsMarkup.actions.prev,
    ]),
    state=[
        States.global_searching,
        States.local_searching,
        States.playlist_tracks,
        States.user_tracks,
        States.playlists],
    chat_type=[types.ChatType.PRIVATE]
)
async def music_navigation(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    current_state = await state.get_state()
    await callback_query.message.edit_reply_markup(
        reply_markup=ResultsMarkup.markup(
            user_id=callback_query.from_user.id,
            callback_data=callback_data,
            back_button=current_state == States.playlist_tracks.state
        )
    )
