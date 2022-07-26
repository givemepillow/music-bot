from aiogram import Bot
from aiovkmusic import Track, Music

from app.core.crud import CRUD
from app.core.services import LRUCache, LockPool
from app.core.services.upload import uploader

cache = LRUCache(capacity=512)
mutex = LockPool()


async def get_file_id(track: Track, music: Music, bot: Bot, crud: CRUD) -> str:
    """
    Возвращает file_id переданной аудиозаписи.
    - 1. Первым шагом проверяет кэш - при попадании сразу возвращает file_id.
    - 2. Если в кэше ничего нет, то проверяет БД -
    при попадании также возвращает file_id.
    - 3. Если и в БД ничего нет, то вызывает uploader, сохраняет аудиозапись
    в БД и затем возвращает file_id.
    :return: file_id - уникальный идентификатор файла в telegram.
    """
    if track.id in cache:
        return cache[track.id]
    file_id = await crud.get_track_file_id(track.id)
    if file_id:
        # Не забываем кэшировать.
        cache[track.id] = file_id
        return file_id
    # Ждём когда освободится мьютекс, если аудиозапись уже скачивается.
    async with await mutex(track.id):
        # Проверяем кэш - вдруг пока мы ждали мьютекс,
        # нужная аудиозапись уже загрузилась в другой таске.
        if track.id in cache:
            return cache[track.id]
        file_id = await uploader(track, music, bot)
        await crud.add_track(
            track_id=track.id,
            file_id=file_id,
            title=track.title,
            artist=track.artist,
            duration=track.duration,
            cover_url=track.cover_url,
            url=track.url
        )
        # Не забываем кэшировать.
        cache[track.id] = file_id
    return file_id
