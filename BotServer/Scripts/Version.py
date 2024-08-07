from httpx import AsyncClient, codes

__version__ = '2.0.2'


async def get_latest_version():
    async with AsyncClient() as client:
        response = await client.get('https://qqbot.ylmty.cc/version.json')
    if response.status_code == codes.OK:
        return response.json()[0]


async def download_version(version: str):
    url = F'https://github.com/Minecraft-QQBot/BotServer/releases/download/v{version}/BotServer-v{version}.zip'
    async with AsyncClient() as client:
        print(F'https://mirror.ghproxy.com/{url}')
        async with client.stream('GET', F'https://mirror.ghproxy.com/{url}') as stream:
            if stream.status_code != codes.OK:
                return False
            with open(F'Download.zip', 'wb') as file:
                async for chunk in stream.aiter_bytes():
                    file.write(chunk)
                return True


if __name__ == '__main__':
    from asyncio import run

    print(run(download_version('2.0.1')))
