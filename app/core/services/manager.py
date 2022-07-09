from aiogram import Bot
from aiovkmusic import Track, Music
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.services import LRUCache
from app.core.services.upload import uploader
from app.db.orm import Session
from app.db import schema as sc

cache = LRUCache(capacity=512)


async def get_file_id(track: Track, music: Music, bot: Bot) -> str:
    """
    Возвращает file_id переданной аудиозаписи.
    - 1. Первым шагом проверяет кэш - при попадании сразу возвращает file_id.
    - 2. Если в кэше ничего нет, то начинает транзакцию и проверяет БД -
    при попадании также возвращает file_id.
    - 3. Если и в БД ничего нет, то вызывает uploader, сохраняет аудиозапись
    в БД и затем возвращает file_id.
    :return: file_id - уникальный идентификатор файла в telegram.
    """
    if track.id in cache:
        return cache[track.id]
    async with Session() as s:
        # Начинаем транзакцию.
        async with s.begin():
            file_id = (await s.execute(
                select(sc.tracks.c.file_id).where(sc.tracks.c.id == track.id)
            )).scalar()
            if file_id:
                # Не забываем кэшировать.
                cache[track.id] = file_id
                return file_id
            file_id = await uploader(track, music, bot)
            insert_track_stmt = insert(sc.tracks).values({
                'id': track.id,
                'file_id': file_id,
                'title': track.title,
                'artist': track.artist,
                'cover_url': track.cover_url,
                'url': track.url
            })
            await s.execute(
                insert_track_stmt.
                on_conflict_do_update(
                    index_elements=['id'],
                    set_=insert_track_stmt.excluded
                ))
            # Не забываем кэшировать.
            cache[track.id] = file_id
            return file_id
