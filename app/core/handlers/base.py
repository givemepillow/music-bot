from app.core.crud import CRUD
from app.core.loader import music
from app.core.services import *
from app.core.states import States
from app.db.orm import Session

crud = CRUD(Session)

playlists = Playlists()

local_music = LocalMusic(Session)
global_music = GlobalMusic(music)
user_music = UserMusic()
user_playlists = UserPlaylists()
playlist_music = PlaylistMusic(music)

music_history = LRUCache(capacity=512)

viewers = {
    'local_music': lambda q: Viewer().make(local_music, q),
    'global_music': lambda q: Viewer().make(global_music, q),
    'playlist_music': lambda m: Viewer().make(playlist_music, m),
    'user_playlists': lambda m: Viewer().make(user_playlists, m),
    'user_music': lambda m: Viewer().make(user_music, m),
}

searchers = {
    States.local_searching.state: lambda q: Viewer().make(local_music, q),
    States.global_searching.state: lambda q: Viewer().make(global_music, q)
}

registry = {}
