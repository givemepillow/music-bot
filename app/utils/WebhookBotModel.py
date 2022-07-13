import os

from aiogram.utils.executor import start_webhook
from loguru import logger

from .AbstractBotModel import AbstractBotModel


class WebhookModel(AbstractBotModel):
    async def on_startup(self, _dispatcher):
        await super().on_startup(_dispatcher)
        await self._bot.set_webhook(os.environ['WEBHOOK_HOST'] + os.environ['WEBHOOK_PATH'])

    async def on_shutdown(self, _dispatcher):
        await super().on_shutdown(_dispatcher)
        await self._bot.delete_webhook()

    def start(self):
        logger.warning("The application is running in webhook mode.")
        start_webhook(
            dispatcher=self._dispatcher,
            webhook_path=os.environ['WEBHOOK_PATH'],
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
            skip_updates=True,
            host=os.environ['WEBAPP_HOST'],
            port=os.environ['WEBAPP_PORT'],
        )
