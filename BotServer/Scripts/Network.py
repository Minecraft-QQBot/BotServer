from io import BytesIO
from httpx import AsyncClient, Client


def request(url: str):
    with Client() as client:
        response = client.get(url)
    if response.status_code == 200:
        return response.json()


async def download(url: str):
    download_bytes = BytesIO()
    async with AsyncClient() as client:
        async with client.stream('GET', 'https://mirror.ghproxy.com/' + url) as stream:
            if stream.status_code != 200:
                return False
            async for chunk in stream.aiter_bytes():
                download_bytes.write(chunk)
            download_bytes.seek(0)
            return download_bytes
