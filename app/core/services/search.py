"""
Данный модуль состоит из 5-ти классов:
Searcher - обрабатывает поисковый запрос и позволяет
ЛЕНИВО итерироваться по результатам запроса;
UserTracksSearcher - аналогичен Searcher'у,
но итерируется по аудиозаписям пользователя
PlaylistTracksSearcher - Аналогичен Searcher'у,
но итерируется по аудиозаписям плейлиста
LocalSearcher - обрабатывает поисковый запрос в БД
и имитирует ленивую итерирацию по результатам запроса;
MusicSearcher - хранит для каждого пользователя своих
Searcher, UserTracksSearcher, PlaylistTracksSearcher и LocalSearcher
"""
from aiovkmusic import Track, Music, Playlist

__all__ = ['MusicSearcher']

from sqlalchemy import select

from app.db.orm import Session
from app.db import schema as sc


class Searcher:
    """
    Данный класс обеспечивает поиск аудиозаписей по текстовому
    запросу и ленивую итерацию по результатам запроса.
    """
    _results: list
    _pages: int
    _step: int
    _music: Music
    _page: int
    _last_page: int
    _initialized: bool

    def _search_generator(self, text: str) -> iter:
        """
        Генератор, обеспечивающий ленивый перебор списка найденных аудиозаписей,
        благодаря тому, что запрос следующей 'пачки' происходит только при вызове
        next() для генератора.
        :param text: текст с названием искомой аудиозаписи.
        """
        for i in range(0, self._step * self._pages, self._step):
            try:
                results = self._music.search(text, count=self._step, offset=i, official_first=True)
                yield results
                if len(results) < self._step:
                    break
            except StopIteration:
                break

    def __init__(self, music: Music, step: int, pages: int):
        """
        :param step: кол-во треков на одном шаге.
        :param pages: кол-во страниц с результатами.
        """
        self._step = step
        self._pages = pages
        self._music = music
        self._page = 0
        self._last_page = 0
        self._initialized = False
        self._results = []

    async def __call__(self, text: str):
        """
        Принимает текстовый запрос на поиск и создаёт генератор для перебора результатов.
        :param text: текст с названием искомой аудиозаписи.
        """
        self._page = 0
        self._last_page = 0
        self._initialized = True
        self._results.clear()
        self._generator = self._search_generator(text)

    def track(self, track_id: int) -> Track:
        """
        Позволяет получить аудиозапись по её id из последних найденных аудиозаписей.
        :raises KeyError - если по указанно id нашлось подходящей аудиозаписи.
        :param track_id: id аудиозаписи.
        """
        for track in self._results:
            if track.id == track_id:
                return track
        raise KeyError("Аудиозаписи с данным id нет в результатах.")

    def next(self) -> list[Track]:
        """
        Возвращает следующие треки по списку, если не превышено кол-во
        страниц и результат ещё имеется - в противном случае возвращает последний результат
        или пустой список, если вообще ничего не было найдено.
        :return: список аудиозаписей.
        """
        if not self._initialized:
            return self._results
        elif self._page == self._last_page:
            try:
                new_results = next(self._generator)
                self._results += new_results
                self._last_page += 1
                self._page += 1
                return new_results
            except StopIteration:
                start = (self._page - 1) * self._step
                return self._results[start: start + self._step]
        else:
            start = self._page * self._step
            self._page += 1
            return self._results[start:start + self._step]

    def prev(self) -> list[Track]:
        """
        Возвращает предыдущие аудиозаписи по списку, если предыдущих нет -
        всегда возвращает первые по списку аудиозаписи.
        :return: список аудиозаписей.
        """
        if self._page > 1:
            self._page -= 1
            start = (self._page - 1) * self._step
            return self._results[start: start + self._step]
        else:
            return self._results[:self._step]


class UserTracksSearcher(Searcher):
    """
    Данный класс обеспечивает получение аудиозаписей пользователя
    и ленивую итерацию по полученным аудиозаписям.
    """

    def _search_generator(self, text: str) -> iter:
        for i in range(0, self._step * self._pages, self._step):
            try:
                results = self._music.user_tracks(count=self._step, offset=i)
                yield results
                if len(results) < self._step:
                    break
            except StopIteration:
                break


class PlaylistTracksSearcher(Searcher):
    """
    Данный класс обеспечивает получение аудиозаписей плейлиста
    и ленивую итерацию по полученным аудиозаписям.
    """

    def _search_generator(self, playlist: Playlist) -> iter:
        for i in range(0, self._step * self._pages, self._step):
            try:
                results = self._music.playlist_tracks(playlist=playlist, count=self._step, offset=i)
                yield results
                if len(results) < self._step:
                    break
            except StopIteration:
                break

    async def __call__(self, playlist: Playlist):
        self._page = 0
        self._last_page = 0
        self._initialized = True
        self._results.clear()
        self._generator = self._search_generator(playlist)


class LocalSearcher:
    """
    Данный класс обеспечивает поиск аудиозаписей по текстовому
    запросу в БД и имитирует ленивую итерацию по результатам запроса.
    """

    async def _search(self, text: str):
        """
        Выполняет запрос в БД и возвращает массив
        подходящих под запрос аудиозаписей.
        :param text: текст с названием искомой аудиозаписи.
        :return:
        """
        async with Session() as s:
            result_rows = [dict(row) for row in (await s.execute(
                select(sc.tracks).where((sc.tracks.c.artist + ' - ' + sc.tracks.c.title).ilike(f'%{text}%'))
            )).all()]
            results = [
                Track(
                    id=track['id'],
                    owner_id=-1,
                    artist=track['artist'],
                    title=track['title'],
                    duration=track['duration'],
                    _covers=[track['cover_url']],
                    url=track['url']
                )
                for track in result_rows
            ]
        return results

    def __init__(self, step: int):
        """
        :param step: кол-во треков на одном шаге.
        """
        self._start = 0
        self._end = step
        self._step = step
        self._initialized = False
        self._results = []

    async def __call__(self, text: str):
        self._start = 0
        self._end = self._step
        self._initialized = True
        self._results = await self._search(text)

    def next(self) -> list[Track]:
        """
        Выполняет сдвиг в массиве и возвращает срез аудиозаписей.
        """
        self._start += self._step
        self._end += self._step
        return self._results[self._start:self._end]

    def prev(self) -> list[Track]:
        """
        Выполняет сдвиг в массиве и возвращает срез аудиозаписей.
        """
        self._start -= self._step
        self._end -= self._step
        return self._results[self._start:self._end]

    def first(self) -> list[Track]:
        """
        Получение первой "пачки" аудиозаписей без сдвига начала и конца.
        """
        return self._results[0:self._step]

    def track(self, track_id: int) -> Track:
        for track in self._results:
            if track.id == track_id:
                return track
        raise KeyError("Аудиозаписи с данным id нет в результатах.")

    @property
    def tracks_count(self):
        """
        :return: количество найденных аудио.
        """
        return len(self._results)


class MusicSearcher:
    """
    Данный класс хранит экземпляр Searcher для каждого user_id.
    """
    _searchers: dict = {}
    _local_searchers: dict = {}
    _user_tracks_searchers: dict = {}
    _playlist_tracks_searchers: dict = {}

    def __init__(
            self,
            music: Music = None,
            step: int = 5,
            pages: int = 5,
            local: bool = False,
            user_tracks: bool = False,
            playlist_tracks: bool = False
    ):
        """
        :param music: экземпляр класса aiovkmusic.Music.
        :param step: кол-во треков на одном шаге.
        :param pages: кол-во страниц с результатами.
        :param local: флаг для создания LocalSearcher
        :param user_tracks: флаг для создания UserTracksSearcher
        :param playlist_tracks: флаг для создания PlaylistTracksSearcher
        """
        self._step = step
        self._pages = pages
        self._music = music
        self._local = local
        self._user_tracks = user_tracks
        self._playlist_tracks = playlist_tracks

    def __getitem__(self, user_id: int) -> Searcher:
        """
        Возвращает экземпляр Searcher, LocalSearcher, UserTracksSearcher
        или PlaylistTracksSearcher для конкретного id и создаёт новый,
        если его ещё нет.
        :param user_id: ID пользователя в Telegram.
        """
        if self._local:
            if user_id not in self._local_searchers:
                self._local_searchers[user_id] = LocalSearcher(self._step)
            return self._local_searchers.get(user_id)
        if self._user_tracks:
            if user_id not in self._user_tracks_searchers:
                self._user_tracks_searchers[user_id] = UserTracksSearcher(self._music, self._step, self._pages)
            return self._user_tracks_searchers.get(user_id)
        if self._playlist_tracks:
            if user_id not in self._playlist_tracks_searchers:
                self._playlist_tracks_searchers[user_id] = PlaylistTracksSearcher(self._music, self._step, self._pages)
            return self._playlist_tracks_searchers.get(user_id)
        else:
            if user_id not in self._searchers:
                self._searchers[user_id] = Searcher(self._music, self._step, self._pages)
            return self._searchers.get(user_id)
