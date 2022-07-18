from aiovkmusic import Music
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.loader import session
from app.db import schema as sc
from app.db.orm import Session


class UserStorage:
    _storage: dict[int: Music] = {}

    @classmethod
    async def put_music(cls, vk_user: str | int, tg_user_id: int):
        # Создаем экземпляр класса Music
        music = Music(user=vk_user, session=session)
        # Если его нет в хранилище, то добавляем
        if tg_user_id not in cls._storage:
            cls._storage[tg_user_id] = music
        async with Session() as s:
            async with s.begin():
                insert_user_stmt = insert(sc.users).values({
                    'id': tg_user_id,
                    'vk_id': music.user_id
                })
                await s.execute(
                    insert_user_stmt.
                    on_conflict_do_update(
                        index_elements=['id'],
                        set_=insert_user_stmt.excluded
                    ))

    @classmethod
    async def get_music(cls, user_id: int) -> Music | None:
        if user_id in cls._storage:
            return cls._storage[user_id]
        async with Session() as s:
            vk_user = (await s.execute(
                select(sc.users.c.vk_id).where(sc.users.c.id == user_id)
            )).scalar()
            # Если бот был перезапущен и в хранилище нет объекта музыки, а в БД есть
            if vk_user:
                music = Music(user=vk_user, session=session)
                cls._storage[user_id] = music
                return music
            return None
