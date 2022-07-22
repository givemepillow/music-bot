import abc
from typing import Callable, Generator

from aiovkmusic import Track


class AbstractViewer:
    def __init__(self):
        self.last_page = 0
        self.page = 0
        self.step = 0
        self.pages = 0
        self.results = []

    @abc.abstractmethod
    def next(self):
        pass

    @abc.abstractmethod
    def prev(self):
        pass

    def get(self, track_id: int) -> Track:
        """
        Позволяет получить аудиозапись по её id из последних найденных аудиозаписей.
        :raises KeyError - если по указанно id нашлось подходящей аудиозаписи.
        :param track_id: id аудиозаписи.
        """
        for track in self.results:
            if track.id == track_id:
                return track
        raise KeyError("Аудиозаписи с данным id нет в результатах.")


class Viewer(AbstractViewer):
    _generator: Generator

    async def make(self, callback: Callable, subject, step=7, pages=5) -> 'Viewer':
        self._generator = await callback(subject, step, pages)
        self.step = step
        self.pages = pages
        return self

    def next(self):
        if self.page == self.last_page:
            try:
                new_results = next(self._generator)
                self.results += new_results
                self.last_page += 1
                self.page += 1
                return new_results
            except StopIteration:
                start = (self.page - 1) * self.step
                return self.results[start: start + self.step]
        else:
            start = self.page * self.step
            self.page += 1
        return self.results[start:start + self.step]

    def prev(self):
        if self.page > 1:
            self.page -= 1
            start = (self.page - 1) * self.step
            return self.results[start: start + self.step]
        else:
            return self.results[:self.step]

    def empty(self):
        if self.page == 0:
            self.next()
            self.prev()
        return not bool(len(self.results))
