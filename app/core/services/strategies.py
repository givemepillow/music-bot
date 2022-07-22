from aiovkmusic import Track
from sqlalchemy import select

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
            result_rows = [dict(row) for row in (await s.execute(
                select(schema.tracks).where((schema.tracks.c.artist + ' - ' + schema.tracks.c.title).ilike(f'%{name}%'))
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
