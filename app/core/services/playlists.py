"""
Данный модуль состоит из 2-х классов: UserPlaylists, хранящий в себе объект
Music (aiovkmusic) конкретного пользователя и его плейлисты,
а также Playlists, хранящий для каждого пользователя свой UserPlaylists
"""

from aiovkmusic import Playlist, Music

from app.core.services.users import UserStorage


class UserPlaylists:
    """
    Данный класс обеспечивает получение плейлистов пользователя.
    """

    def __init__(self, music: Music):
        self._music = music
        self._results = self._music.playlists()

    def get_playlist_by_id(self, playlist_id: int) -> Playlist:
        for playlist in self._results:
            if playlist.id == playlist_id:
                return playlist
        raise KeyError("Плейлиста с данным id нет в результатах.")

    def get_playlists(self) -> list[Playlist]:
        return self._results


class Playlists:
    """
    Данный класс хранит экземпляр Playlists для каждого user_id.
    """
    _playlists: dict = {}

    async def __call__(self, user_id: int) -> UserPlaylists:
        """
        Получает экземляр класса Music для конкретного пользователя
        и возвращает экземпляр класса UserPlaylists этого пользователя.
        :param user_id: ID пользователя в Telegram.
        """
        _music = await UserStorage.get_music(user_id)
        self._playlists[user_id] = UserPlaylists(music=_music)
        return self._playlists[user_id]
