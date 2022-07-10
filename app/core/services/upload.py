import os

import aiofiles
from aiofiles import os as async_os
from aiogram import Bot
from aiovkmusic import Track, Music

# Папка для временных файлов.
PATH = 'downloads'
# Группа в которую бот будет отправлять всю скаченную музыку.
TARGET_CHAT_ID = os.environ['MEDIA_CHAT']


async def uploader(track: Track, music: Music, bot: Bot) -> str:
    """
    Скачивает музыку на диск, затем отправляет её в telegram и удаляет
    после получения file_id.
    :return file_id - уникальный идентификатор файла в telegram.
    """
    await music.download(track, path=f"{PATH}")
    async with aiofiles.open(track.path, 'rb') as file:
        audiofile = await file.read()
        sent_audio = await bot.send_audio(
            TARGET_CHAT_ID,
            audio=audiofile,
            performer=track.artist,
            title=track.title,
            thumb=track.cover_url
        )
        file_id = sent_audio.audio.file_id
    await async_os.remove(track.path)
    return file_id
