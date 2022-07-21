from math import ceil

from aiogram import types
from aiogram.types import Message

from app.core.extensions import MessageBox
from app.core.handlers.base import local_searcher
from app.core.loader import dp
from app.core.markups.inline import SearchResultsMarkup
from app.core.states import States


@dp.message_handler(state=States.local_searching, chat_type=[types.ChatType.PRIVATE])
async def local_search(message: Message):
    """
    Хендлер для поиска уже загруженной музыки в базе данных
    и вывода инлайн-меню со списком найденных треков.
    :param message: поисковой запрос.
    """
    _user_id = message.from_user.id
    await MessageBox.delete_last(_user_id)

    await local_searcher[_user_id](message.text)
    tracks_count = local_searcher[_user_id].tracks_count

    count = 7
    if tracks_count >= 35:
        pages = 5
    elif tracks_count <= 7:
        pages = 1
    else:
        pages = ceil(tracks_count / count)

    tracks = local_searcher[_user_id].first()

    SearchResultsMarkup.setup(
        tracks=tracks,
        user_id=_user_id,
        searcher_generator=local_searcher[_user_id],
        count=count,
        pages=pages
    )

    _text = ''
    if len(tracks):
        _text = f'Треки по запросу <b>«{message.text}»</b>:'
    else:
        _text = f'По запросу <b>«{message.text}»</b> ничего не найдено :('

    _message = await message.answer(
        text=_text + '\nНе нашли, что искали? Попробуйте поиск по <b>ВК</b> – /global',
        reply_markup=SearchResultsMarkup.markup(user_id=_user_id),
        parse_mode="HTML"
    )
    MessageBox.put(_message, _user_id)
