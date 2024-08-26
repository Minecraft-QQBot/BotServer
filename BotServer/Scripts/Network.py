# 导入必要的库和模块
import psutil
from hashlib import md5
from io import BytesIO
from httpx import AsyncClient

from nonebot.log import logger

from Globals import uuid_caches

# 创建异步客户端，用于HTTP请求
client = AsyncClient()


# 定义异步函数request，用于发送HTTP GET请求并返回JSON响应
async def request(url: str):
    response = await client.get(url)
    if response.status_code == 200:
        return response.json()


# 定义异步函数get_player_uuid，用于获取Minecraft玩家的UUID
async def get_player_uuid(name: str):
    # 首先检查缓存中是否存在该玩家的UUID
    if name in uuid_caches:
        return uuid_caches[name]
    # 默认UUID，用于在查询失败时返回
    uuid = '8667ba71b85a4004af54457a9734eed7'
    # 发送请求获取玩家的UUID
    if response := await request(F'https://api.mojang.com/users/profiles/minecraft/{name}'):
        uuid = (response.get('id') or '8667ba71b85a4004af54457a9734eed7')
    # 将获取的UUID缓存
    uuid_caches[name] = uuid
    return uuid


# 定义异步函数send_bot_status，用于发送机器人的在线状态
async def send_bot_status(status: bool):
    # 获取网卡的MAC地址
    mac = None
    addresses = psutil.net_if_addrs()
    for interface_name, interface_address in addresses.items():
        for address in interface_address:
            if address.family == psutil.AF_LINK:
                mac = address.address
        if mac: break
    # 生成机器人的唯一ID
    bot_id = md5((mac + 'Minecraft_QQBot').encode())
    data = {'bot_id': bot_id.hexdigest(), 'status': status}
    # 发送状态改变请求
    response = await client.get('http://api.qqbot.bugjump.xyz/status/change', params=data)
    if response.status_code == 200:
        logger.success('发送机器人状态改变信息成功！')
        return True
    logger.warning('无法连接上服务器！发送机器人状态改变信息失败。')
    return False


# 定义异步函数download，用于下载指定URL的文件内容
async def download(url: str):
    download_bytes = BytesIO()
    async with client.stream('GET', 'https://mirror.ghproxy.com/' + url) as stream:
        if stream.status_code != 200:
            return False
        async for chunk in stream.aiter_bytes():
            download_bytes.write(chunk)
        download_bytes.seek(0)
        return download_bytes
