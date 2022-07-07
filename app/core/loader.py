import argparse
import os

from aiovkmusic import Music, VKSession

from app.utils import WebhookModel, PollingModel

__all__ = ['dp', 'bot_engine', 'bot', 'memory_storage', 'music']

parser = argparse.ArgumentParser("main.py")

parser.add_argument("--mode", "-m", nargs=1,
                    help="Run the application in polling mode or webhook mode.",
                    default='polling',
                    choices=['polling', 'webhook']
                    )

args = parser.parse_args()

bot_engine = WebhookModel() if args.mode[0] == 'webhook' else PollingModel()

memory_storage = bot_engine.get_storage()
dp = bot_engine.get_dispatcher()
bot = bot_engine.get_bot()

login, password = os.environ.get('VK_ACC').split(':')
session = VKSession(
    login=login,
    password=password,
    session_file_path='session.json'
)
music = Music(user=os.environ.get('VK_LINK'), session=session)
