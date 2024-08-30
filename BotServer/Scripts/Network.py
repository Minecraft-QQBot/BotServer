from hashlib import md5
from io import BytesIO

import psutil
from httpx import AsyncClient
from nonebot.log import logger

from Scripts.Globals import uuid_caches

client = AsyncClient()


async def request(url: str):
    try:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        logger.warning(F'请求 {url} 失败：错误的状态代码 {response.status_code}')
        return None
    except Exception as error:
        logger.warning(F'请求 {url} 失败：{error}')


async def get_player_uuid(name: str):
    if name in uuid_caches:
        return uuid_caches[name]
    uuid = '8667ba71b85a4004af54457a9734eed7'
    if response := await request(F'https://api.mojang.com/users/profiles/minecraft/{name}'):
        uuid = (response.get('id') or '8667ba71b85a4004af54457a9734eed7')
    uuid_caches[name] = uuid
    return uuid


async def send_bot_status(status: bool):
    mac = None
    addresses = psutil.net_if_addrs()
    for interface_name, interface_address in addresses.items():
        for address in interface_address:
            if address.family == psutil.AF_LINK:
                mac = address.address
        if mac: break
    bot_id = md5((mac + 'Minecraft_QQBot').encode())
    data = {'bot_id': bot_id.hexdigest(), 'status': status}
    response = await client.get('http://api.qqbot.bugjump.xyz/status/change', params=data)
    if response.status_code == 200:
        logger.success('发送机器人状态改变信息成功！')
        return True
    logger.warning('无法连接上服务器！发送机器人状态改变信息失败。')
    return False


async def download(url: str):
    download_bytes = BytesIO()
    url = (('https://mirror.ghproxy.com/' + url) if 'github' in url else url)
    async with client.stream('GET', url) as stream:
        if stream.status_code != 200:
            return False
        async for chunk in stream.aiter_bytes():
            download_bytes.write(chunk)
        download_bytes.seek(0)
        return download_bytes
