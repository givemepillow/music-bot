import sys
import warnings

import loguru

from app.core.handlers import dp as dispatcher
from app.core.loader import bot_engine

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
loguru.logger.remove()
loguru.logger.add(
    sink=sys.stdout,
    format="{time:MMM DD HH:mm:ss.SSS}: {message}",
    enqueue=True
)

if __name__ == '__main__':
    loguru.logger.info(
        f"Number of message handlers: {len(dispatcher.message_handlers.handlers)}."
    )
    loguru.logger.info(
        f"Number of callback query handlers: {len(dispatcher.callback_query_handlers.handlers)}."
    )
    bot_engine.start()
