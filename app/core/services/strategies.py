from aiovkmusic import Track
from sqlalchemy import select, or_
import transliterate

from app.db import schema


class GlobalMusic:
    def __init__(self, music):
        self.music = music

    async def __call__(self, query, step, pages):
        def generator():
            for i in range(0, pages):
                try:
                    tracks = self.music.search(query, count=step, offset=i * step, official_first=True)
                    yield tracks
                    if len(tracks) < step:
                        break
                except StopIteration:
                    break

        return generator()


class LocalMusic:
    ru = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    delimiters = {'  ', '-', '!', '.', '*', '/', '+', '(', ')'}
    dualities = set('zsckiy')

    def __init__(self, session):
        self.session = session

    async def __call__(self, query, step, pages):
        tracks = await self.get_tracks_by_name(query)

        def generator():
            for i in range(0, pages):
                try:
                    results = tracks[i * step: (i * step) + step]
                    yield results
                    if len(results) < step:
                        break
                except (KeyError, StopIteration):
                    break

        return generator()

    async def get_tracks_by_name(self, name: str):
        async with self.session() as s:
            stmt = self._statement_builder(name.replace('_', ' '))
            result_rows = [dict(row) for row in (await s.execute(stmt)).all()]
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

        results.sort(key=lambda track: self._sort_condition(name, track), reverse=True)
        return results

    def _sort_condition(self, name, track: Track):
        patterns = self._remove_delimiters(name.lower()).split()
        _track = f" {' '.join((track.artist, track.title)).lower()} "
        return sum((f" {p} " in _track for p in patterns)), sum((p in _track for p in patterns))

    def _remove_delimiters(self, text):
        return ''.join([ch if ch not in self.delimiters else ' ' for ch in text]).strip()

    def _duality(self, text):
        _text = ''.join([ch if ch not in self.dualities else '_' for ch in text]).strip()
        return text if len(set(self._remove_delimiters(_text).replace(' ', ''))) == 1 else _text

    def _name_patterns(self, name: str):
        is_ru = not self.ru.isdisjoint(name.lower())
        transliterate_name = transliterate.translit(
            name,
            language_code='ru',
            reversed=is_ru
        )
        duality_name = self._duality(transliterate_name) if is_ru else self._duality(name)
        return {
            name,
            transliterate_name,
            duality_name,
            self._remove_delimiters(name),
            self._remove_delimiters(transliterate_name),
            *name.split(),
            *transliterate_name.split()
        }

    def _statement_builder(self, name):
        params = self._name_patterns(name)
        conditions = []
        for p in params:
            conditions.append((schema.tracks.c.artist + ' ' + schema.tracks.c.title)
                              .ilike(f'%{p}%'))
        return select(schema.tracks).where(or_(*conditions))


class UserMusic:
    async def __call__(self, user_music, step, pages):
        def generator():
            for i in range(0, step * pages, step):
                try:
                    results = user_music.user_tracks(count=step, offset=i)
                    yield results
                    if len(results) < step:
                        break
                except StopIteration:
                    break

        return generator()


class PlaylistMusic:
    def __init__(self, music):
        self.music = music

    async def __call__(self, playlist, step, pages):
        def generator():
            for i in range(0, step * pages, step):
                try:
                    results = self.music.playlist_tracks(playlist=playlist, count=step, offset=i)
                    yield results
                    if len(results) < step:
                        break
                except StopIteration:
                    break

        return generator()


class UserPlaylists:

    async def __call__(self, user_music, step, pages):
        playlists = user_music.playlists()

        def generator():
            for i in range(0, pages):
                try:
                    results = playlists[i * step: (i * step) + step]
                    yield results
                    if len(results) < step:
                        break
                except (KeyError, StopIteration):
                    break

        return generator()
