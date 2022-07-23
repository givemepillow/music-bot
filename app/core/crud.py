from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db import schema as sc


class CRUD:
    def __init__(self, session):
        self.session = session

    async def get_track_file_id(self, track_id):
        async with self.session() as s:
            return (await s.execute(
                select(sc.tracks.c.file_id).where(sc.tracks.c.id == track_id)
            )).scalar()

    async def add_track(self, track_id, file_id, title, artist, duration, cover_url, url):
        async with self.session() as s:
            async with s.begin():
                insert_track_stmt = insert(sc.tracks).values({
                    'id': track_id,
                    'file_id': file_id,
                    'title': title,
                    'artist': artist,
                    'duration': duration,
                    'cover_url': cover_url,
                    'url': url
                })
                await s.execute(
                    insert_track_stmt.
                    on_conflict_do_update(
                        index_elements=['id'],
                        set_=insert_track_stmt.excluded
                    ))
