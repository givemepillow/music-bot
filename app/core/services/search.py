"""
Данный модуль состоит из 2-х классов: Searcher - обрабатывает поисковый запрос
и позволяющий ЛЕНИВО итерироваться по результатам запроса и MusicSearcher -
хранит для каждого пользователя свой Searcher.
"""
from aiovkmusic import Track, Music

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


class LocalSearcher:
    async def _search(self, text: str):
        async with Session() as s:
            result_rows = [dict(row) for row in (await s.execute(
                select(sc.tracks).where((sc.tracks.c.artist + ' - ' + sc.tracks.c.title).ilike(f'%{text}%'))
            )).all()]
            self._results = [
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

    def __init__(self, step: int, pages: int):
        self._start = 0
        self._end = step
        self._step = step
        self._pages = pages
        self._initialized = False
        self._results = []

    async def __call__(self, text: str):
        self._start = 0
        self._end = self._step
        self._initialized = True
        await self._search(text)

    def next(self) -> list[Track]:
        self._start += self._step
        self._end += self._step
        return self._results[self._start:self._end]

    def prev(self) -> list[Track]:
        self._start -= self._step
        self._end -= self._step
        return self._results[self._start:self._end]

    def first(self) -> list[Track]:
        return self._results[0:self._step]

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

    @property
    def tracks_count(self):
        return len(self._results)


class MusicSearcher:
    """
    Данный класс хранит экземпляр Searcher для каждого user_id.
    """
    _searchers: dict = {}
    _local_searchers: dict = {}

    def __init__(self, music: Music = None, step: int = 5, pages: int = 5, local: bool = False):
        """
        :param music: экземпляр класса aiovkmusic.Music.
        :param step: кол-во треков на одном шаге.
        :param pages: кол-во страниц с результатами.
        """
        self._step = step
        self._pages = pages
        self._music = music
        self._local = local

    def __getitem__(self, user_id: int) -> Searcher:
        """
        Возвращает экземпляр Searcher для конкретного id и создаёт новый,
        если его ещё нет.
        :param user_id: telegram id пользователя.
        """
        if not self._local:
            if user_id not in self._searchers:
                self._searchers[user_id] = Searcher(self._music, self._step, self._pages)
            return self._searchers.get(user_id)
        else:
            if user_id not in self._local_searchers:
                self._local_searchers[user_id] = LocalSearcher(self._step, self._pages)
            return self._local_searchers.get(user_id)
