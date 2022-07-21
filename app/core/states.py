from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    searching = State()
    setting_link = State()
    local_searching = State()
    profile = State()
    user_audios = State()
    playlists = State()
    playlist_tracks = State()
