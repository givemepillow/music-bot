from aiogram import Bot
from aiovkmusic import Track, Music
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.services import LRUCache, LockTable
from app.core.services.upload import uploader
from app.db import schema as sc
from app.db.orm import Session

cache = LRUCache(capacity=512)
downloading = LockTable()


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
        async with s.begin():
            file_id = (await s.execute(
                select(sc.tracks.c.file_id).where(sc.tracks.c.id == track.id)
            )).scalar()
            if file_id:
                # Не забываем кэшировать.
                cache[track.id] = file_id
                return file_id
            # Проверяем не скачивается ли в данный момент нужная нам аудиозапись.
            # if track.id not in downloading:
            #     # Создаём мьютекс для скачиваемой аудиозаписи.
            #     downloading[track.id] = asyncio.Lock()
            # Ждём когда освободится мьютекс, если аудиозапись уже скачивается.
            async with downloading[track.id]:
                # Проверяем кэш - вдруг пока мы ждали мьютекс,
                # нужная аудиозапись уже загрузилась в другой таске.
                if track.id in cache:
                    del downloading[track.id]
                    return cache[track.id]
                file_id = await uploader(track, music, bot)
                insert_track_stmt = insert(sc.tracks).values({
                    'id': track.id,
                    'file_id': file_id,
                    'title': track.title,
                    'artist': track.artist,
                    'duration': track.duration,
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
                del downloading[track.id]
        return file_id
