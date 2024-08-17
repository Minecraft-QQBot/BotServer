import psutil
from hashlib import sha512
from io import BytesIO
from httpx import AsyncClient, Client

from nonebot.log import logger

from .Managers.Temp import temp_manager


def request(url: str):
    with Client() as client:
        response = client.get(url)
    if response.status_code == 200:
        return response.json()


def get_player_uuid(name: str):
    if name in temp_manager.player_uuid:
        return temp_manager.player_uuid[name]
    response = request(F'https://api.mojang.com/users/profiles/minecraft/{name}')
    if uuid := response.get('id'):
        temp_manager.player_uuid[name] = uuid
        return uuid


def send_bot_status(status: bool):
    mac = None
    addresses = psutil.net_if_addrs()
    for interface_name, interface_address in addresses.items():
        for address in interface_address:
            if address.family == psutil.AF_LINK:
                mac = address.address
    bot_id = sha512((mac + 'Minecraft_QQBot').encode())
    with Client() as client:
        data = {'bot_id': bot_id.hexdigest(), 'status': status}
        response = client.post('http://api.qqbot.bugjump.xyz/status/change', data=data)
        if response.status_code == 200:
            logger.success('发送机器人状态改变信息成功！')
            return True
    logger.warning('无法连接上服务器！发送机器人状态改变信息失败。')
    return False


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
