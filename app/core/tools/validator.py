import aiohttp


async def validate_link(link: str):
    if (link.startswith('https://vk.com') or link.startswith('http://vk.com')) and len(link) > 15:
        pass
    elif link.startswith('vk.com') and len(link) > 7:
        link = 'https://' + link
    elif link.isdigit():
        link = f'https://vk.com/id{link}'
    else:
        link = f'https://vk.com/{link}'

    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 404:
                return False
            else:
                return True
