from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    global_searching = State()
    setting_link = State()
    local_searching = State()
    profile = State()
    user_tracks = State()
    playlists = State()
    playlist_tracks = State()
