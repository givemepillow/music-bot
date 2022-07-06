import os
from abc import abstractmethod

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from .Singletone import SingletonABC


class AbstractBotModel(SingletonABC):

    def __init__(self):
        self._bot = Bot(token=os.environ.get('BOT_TOKEN'))
        self._memory_storage = MemoryStorage()
        self._dispatcher = Dispatcher(self._bot, storage=self._memory_storage)
        self._dispatcher.middleware.setup(LoggingMiddleware())

    def get_dispatcher(self):
        return self._dispatcher

    def get_bot(self):
        return self._bot

    def get_storage(self):
        return self._memory_storage

    @abstractmethod
    async def on_startup(self, _dispatcher):
        pass

    @abstractmethod
    async def on_shutdown(self, _dispatcher):
        logger.info("Closing storage...")
        await _dispatcher.storage.close()
        await _dispatcher.storage.wait_closed()
        logger.info("Bot shutdown...")

    @abstractmethod
    def start(self):
        pass
