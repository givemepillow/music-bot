from aiogram import types
from aiogram.types import CallbackQuery, Message

from app.core.handlers.templates import show_playlists
from app.core.loader import dp, bot
from app.core.markups.inline import SearchResultsMarkup
from app.core.services import MusicSearcher
from app.core.services.users import UserStorage
from app.core.states import States


@dp.callback_query_handler(state=[States.profile], chat_type=[types.ChatType.PRIVATE])
async def profile_buttons(callback_query: CallbackQuery):
    """
    Хендлер обработки нажатий на кнопки в профиле.
    :param callback_query: Callback Query
    """
    await callback_query.answer()
    tg_user_id = callback_query.from_user.id

    if callback_query.data == 'change':
        await bot.send_message(chat_id=tg_user_id, text='Введите ссылку на страницу (или ID):')
        await States.setting_link.set()

    if callback_query.data == 'audios':
        music = await UserStorage.get_music(tg_user_id)
        user_tracks_searcher = MusicSearcher(music, 10, 100, user_tracks=True)
        await user_tracks_searcher[tg_user_id]('_')
        tracks = user_tracks_searcher[tg_user_id].next()
        SearchResultsMarkup.setup(
            tracks=tracks,
            user_id=tg_user_id,
            searcher_generator=user_tracks_searcher[tg_user_id]
        )
        _text = ''
        if len(tracks):
            _text = 'Ваши <b>аудиозаписи</b>:'
        else:
            _text = 'Аудиозаписей нет :('
        await bot.send_message(
            chat_id=tg_user_id,
            text=_text,
            reply_markup=SearchResultsMarkup.markup(user_id=tg_user_id),
            parse_mode='HTML'
        )
        await bot.send_message(
            chat_id=tg_user_id,
            text='Чтобы вернуться к поиску, используйте следующие команды:\n'
                 '  <b>• /global</b> – для поиска по ВК\n'
                 '  <b>• /local</b> – для поиска по базе данных\n',
            parse_mode='HTML'
        )
        await States.user_audios.set()

    if callback_query.data == 'playlists':
        await show_playlists(tg_user_id)


@dp.message_handler(
    state=[States.user_audios, States.playlist_tracks, States.playlists],
    chat_type=[types.ChatType.PRIVATE]
)
async def back_handler(message: Message):
    """
    Хендлер обработки сообщений, введенных
    пользователем не в состоянии поиска.
    :param message: сообщение пользователя.
    """
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Чтобы вернуться к поиску, используйте следующие команды:\n'
             '  <b>• /global</b> – для поиска по ВК\n'
             '  <b>• /local</b> – для поиска по базе данных\n',
        parse_mode='HTML'
    )
