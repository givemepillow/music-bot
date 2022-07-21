from aiogram import types
from aiogram.types import Message, CallbackQuery

from app.core.extensions import MessageBox
from app.core.handlers.base import searcher
from app.core.loader import dp
from app.core.markups.inline import *
from app.core.states import States


@dp.message_handler(state=States.searching, chat_type=[types.ChatType.PRIVATE])
async def music_search(message: Message):
    """
    Хендлер для поиска музыки и вывода инлайн-меню со списком найденных треков.
    :param message: поисковой запрос.
    """
    _user_id = message.from_user.id
    await MessageBox.delete_last(_user_id)

    await searcher[_user_id](message.text)
    tracks = searcher[_user_id].next()

    SearchResultsMarkup.setup(tracks=tracks, user_id=_user_id, searcher_generator=searcher[_user_id])

    _text = ''
    if len(tracks):
        _text = f'Треки по запросу <b>«{message.text}»</b>:'
    else:
        _text = f'По запросу <b>«{message.text}»</b> ничего не найдено :('

    _message = await message.answer(
        text=_text + '\nНе нашли, что искали? Попробуйте локальный поиск – /local',
        reply_markup=SearchResultsMarkup.markup(user_id=_user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, _user_id)


@dp.callback_query_handler(
    SearchResultsMarkup.data.filter(action=[SearchResultsMarkup.actions.next, SearchResultsMarkup.actions.prev]),
    state=[States.searching, States.local_searching, States.user_audios, States.playlist_tracks],
    chat_type=[types.ChatType.PRIVATE]
)
async def music_list_navigation(callback_query: CallbackQuery, callback_data: dict):
    """
    Хендлер навигации по списку найденных треков.
    :param callback_query: Callback Query
    :param callback_data: Callback Data
    """
    await callback_query.message.edit_reply_markup(
        reply_markup=SearchResultsMarkup.markup(
            user_id=callback_query.from_user.id, callback_data=callback_data
        )
    )


@dp.message_handler(chat_type=[types.ChatType.PRIVATE])
async def start_handler(message: Message):
    """
    Хендлер запуска бота.
    :param message: сообщение пользователя.
    """
    await message.answer(
        text='Ничего не понятно – может быть вы хотели найти какую-нибудь аудиозапись <b>/start</b>?',
        parse_mode='HTML'
    )
