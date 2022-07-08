from urllib.parse import urlparse

import aiohttp
import validators


async def validate_link(link: str):
    if not link.startswith('https://') and not link.startswith('http://'):
        link = 'https://' + link
    if not validators.url(link):
        link = f'https://vk.com/{link.replace("https://", "")}'
    parsed_link = urlparse(link)
    if parsed_link.netloc != 'vk.com' or len(parsed_link.path) <= 1:
        return False

    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 404:
                return False
            else:
                return True
