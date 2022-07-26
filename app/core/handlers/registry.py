from app.core.handlers import message_handlers as msg_handlers
from app.core.handlers import callback_query_handler as cb_handlers
from app.core.loader import dp
from aiogram import types as tg_types

from app.core.markups.inline import ResultsMarkup
from app.core.states import States

dp.register_message_handler(
    msg_handlers.StartCommandHandler(),
    commands='start',
    state='*',
    chat_type=[tg_types.ChatType.PRIVATE]
)

dp.register_message_handler(
    msg_handlers.LinkCommandHandler(),
    commands='link',
    state='*',
    chat_type=[tg_types.ChatType.PRIVATE]
)
dp.register_message_handler(
    msg_handlers.ProfileCommandHandler(),
    commands=['profile', 'id'],
    state='*',
    chat_type=[tg_types.ChatType.PRIVATE]
)

dp.register_message_handler(
    msg_handlers.LocalCommandHandler(),
    commands='local',
    state='*',
    chat_type=[tg_types.ChatType.PRIVATE]
)

dp.register_message_handler(
    msg_handlers.GlobalCommandHandler(),
    commands=['global', 'search'],
    state='*',
    chat_type=[tg_types.ChatType.PRIVATE]
)

dp.register_message_handler(
    msg_handlers.UpdateLinkHandler(),
    state=States.setting_link,
    chat_type=[tg_types.ChatType.PRIVATE]
)

dp.register_callback_query_handler(
    cb_handlers.MusicSenderHandler(),
    ResultsMarkup.data.filter(action=ResultsMarkup.actions.select),
    state=[States.global_searching, States.local_searching, States.playlist_tracks, States.user_tracks],
    chat_type=[tg_types.ChatType.PRIVATE]
)
