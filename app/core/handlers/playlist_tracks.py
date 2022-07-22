from aiogram import types
from aiogram.types import CallbackQuery

from app.core.handlers.base import playlists
from app.core.handlers.templates import show_playlists
from app.core.loader import bot, dp
from app.core.markups.inline import PlaylistsMarkup, SearchResultsMarkup
from app.core.services import MusicSearcher
from app.core.services.users import UserStorage
from app.core.states import States


@dp.callback_query_handler(
    PlaylistsMarkup.data.filter(action=PlaylistsMarkup.actions.select),
    state=States.playlists,
    chat_type=[types.ChatType.PRIVATE]
)
async def playlist_tracks(callback_query: CallbackQuery, callback_data: dict):
    """
    Хендлер для вывода инлайн-меню со списком треков из выбранного плейлиста.
    :param callback_data: Callback Data
    :param callback_query: Callback Query
    """
    await callback_query.answer()
    _user_id = callback_query.from_user.id
    _music = await UserStorage.get_music(user_id=_user_id)

    playlist_id = int(callback_data['playlist_id'])
    user_playlists = await playlists(_user_id)
    playlist = user_playlists.get_playlist_by_id(playlist_id)

    playlist_tracks_searcher = MusicSearcher(_music, 7, 5, playlist_tracks=True)
    await playlist_tracks_searcher[_user_id](playlist)
    tracks = playlist_tracks_searcher[_user_id].next()

    SearchResultsMarkup.setup(tracks=tracks, user_id=_user_id, searcher_generator=playlist_tracks_searcher[_user_id])

    _text = ''
    if len(tracks):
        _text = f'Треки из плейлиста <b>«{playlist.title}»</b>:'
    else:
        _text = f'В плейлисте <b>«{playlist.title}»</b> нет треков :('

    _message = await bot.send_message(
        chat_id=_user_id,
        text=_text,
        reply_markup=SearchResultsMarkup.markup(user_id=_user_id, back_button=True),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=_user_id,
        text='Чтобы вернуться к поиску, используйте следующие команды:\n'
             '  <b>• /global</b> – для поиска по ВК\n'
             '  <b>• /local</b> – для поиска по базе данных\n',
        parse_mode='HTML'
    )
    await States.playlist_tracks.set()


@dp.callback_query_handler(
    PlaylistsMarkup.data.filter(action=[PlaylistsMarkup.actions.next, PlaylistsMarkup.actions.prev]),
    state=[States.playlists],
    chat_type=[types.ChatType.PRIVATE]
)
async def playlists_list_navigation(callback_query: CallbackQuery, callback_data: dict):
    """
    Хендлер навигации по списку плейлистов.
    :param callback_query: Callback Query
    :param callback_data: Callback Data
    """
    markup, text = PlaylistsMarkup.markup(user_id=callback_query.from_user.id, callback_data=callback_data)
    await callback_query.message.edit_text(text=text, parse_mode='HTML')
    await callback_query.message.edit_reply_markup(reply_markup=markup)


@dp.callback_query_handler(
    SearchResultsMarkup.data.filter(action=[SearchResultsMarkup.actions.back]),
    state=[States.playlist_tracks],
    chat_type=[types.ChatType.PRIVATE]
)
async def back_from_playlist_tracks(callback_query: CallbackQuery):
    """
    Хендлер возврата к плейлистам из треков плейлиста.
    :param callback_query: Callback Query
    """
    await callback_query.answer()
    user_id = callback_query.from_user.id
    await show_playlists(user_id)
