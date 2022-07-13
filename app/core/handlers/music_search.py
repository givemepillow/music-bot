from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from app.core.extensions import MessageBox
from app.core.loader import dp, music
from app.core.markups.inline import *
from app.core.services.search import *
from app.core.states import States

searcher = MusicSearcher(music, 7, 5)


@dp.message_handler(state=States.searching, chat_type=[types.ChatType.PRIVATE])
async def music_search(message: Message):
    """
    Хендлер для поиска музыки и вывода инлайн-меню со списком найденных треков.
    :param message: поисковой запрос
    """
    _user_id = message.from_user.id
    await MessageBox.delete_last(_user_id)

    searcher[_user_id](message.text)
    tracks = searcher[_user_id].next()

    SearchResultsMarkup.setup(tracks=tracks, user_id=_user_id, searcher_generator=searcher[_user_id])

    _text1 = f'Треки по запросу <b>«{message.text}»</b>:'
    _text2 = f'По запросу <b>«{message.text}»</b> ничего не найдено :('

    _message = await message.answer(
        text=_text1 if len(tracks) else _text2,
        reply_markup=SearchResultsMarkup.markup(user_id=_user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, _user_id)


@dp.callback_query_handler(
    SearchResultsMarkup.data.filter(action=[SearchResultsMarkup.actions.next, SearchResultsMarkup.actions.prev]),
    state=States.searching,
    chat_type=[types.ChatType.PRIVATE]
)
async def music_list_navigation(callback_query: CallbackQuery, callback_data: CallbackData):
    """
    Хендлер навигации по списку найденных треков.
    :param callback_query: Callback Query
    :param callback_data: Callback Data
    """
    _user_id = callback_query.from_user.id
    await callback_query.message.edit_reply_markup(
        reply_markup=SearchResultsMarkup.markup(
            user_id=_user_id, callback_data=callback_data
        )
    )
