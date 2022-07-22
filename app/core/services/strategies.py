from aiovkmusic import Track
from sqlalchemy import select

from app.core.loader import music
from app.db.orm import Session
from app.db import schema


class GlobalMusic:
    async def __call__(self, query, step, pages):
        def generator():
            for i in range(0, pages):
                try:
                    tracks = music.search(query, count=step, offset=i * step, official_first=True)
                    yield tracks
                    if len(tracks) < step:
                        break
                except StopIteration:
                    break

        return generator()


class LocalMusic:

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

    @staticmethod
    async def get_tracks_by_name(name: str):
        async with Session() as s:
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
    pass


class UserPlaylists:
    pass
