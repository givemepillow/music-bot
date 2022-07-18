from math import ceil

from aiogram.types import Message

from app.core.extensions import MessageBox
from app.core.handlers.base import local_searcher
from app.core.loader import dp
from app.core.markups.inline import SearchResultsMarkup
from app.core.states import States


@dp.message_handler(commands='local', state='*')
async def local_search_command(message: Message):
    await message.answer(text='Поиск треков по сохраненным в базе данных...')
    await States.local_searching.set()


@dp.message_handler(state=States.local_searching)
async def local_search(message: Message):
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
