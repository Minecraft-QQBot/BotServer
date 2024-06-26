# Minecraft_QQBot

**一款通过 MCDReforged 插件与 Minecraft 交互的 Python QQ 机器人**。功能丰富，使用简单且可以自行配置，仅需简单配置即可使用。目前已实现的功能有：

- !!qq 指令在游戏内向 QQ 群发送消息。
- 把 QQ 群内的消息转发到游戏内。
- 禁用 QQ 群内的特定命令。
- 对 QQ 群指令相应。目前已实现的指令有：
  - `luck` 查看今日幸运指数。
  - `list` 查询每个服务器的玩家在线情况。
  - `help` 查看帮助信息。
  - `server` 查看当前在线的服务器并显示对应编号。

更多功能还在探索中……

## 使用

因为本插件依赖于 MCDR 所以请先安装，[官网](https://mcdreforged.com/zh-CN) 在这里。若安装完 MCDR 后，则可以下载本项目。

你可以到 [Releases](https://github.com/Xiaocaicai/Minecraft_QQBot/releases) 下载最新版本的机器人服务器和服务器插件。

在命令行内输入以下指令安装依赖：

```bash
pip3 install "nonebot2[fastapi], nonebot-adapter-onebot, mcdreforged"
```

### 配置环境

解压在 Releases 中下载的 `BotServer.zip` 到任意位置，进入 `BotServer` 文件夹，编辑文件夹下的 `.env` 文件，按照注释配置即可。

对于 QQ 机器人平台（如 GoCqHttp，LOneBot 等）的配置请见 [Onebot](https://onebot.adapters.nonebot.dev/docs/guide/setup)
适配器文档。

> 本机器人仅支持 `Websocket` 反向链接，并且仅支持 Onebot V11 协议。

### 安装插件

将下载好的 `QQChat.mcdr` 文拷贝到 MCDR 的 插件文件夹 下，编辑 配置文件夹 QQChat 下的 `Config.json` 文件。配置文件内容参考如下：

```json
{
  "name": "服务器名称",
  "port": 8000,
  "token": "令牌",
  "broadcast_server": true,
  "broadcast_player": true
}
```

其中各个字段的含义如下：

|      字段名      |  类型  |                       含义                       |
| :--------------: | :----: | :----------------------------------------------: |
|       port       |  整数  | 端口号，和服务器配置文件下的 PORT 保持一致即可。 |
|       name       | 字符串 |             服务器名称，中英文都可。             |
|      token       | 字符串 | 口令，和服务器配置文件下的 TOKEN 保持一致即可。  |
| broadcast_player | 布尔值 |     是否播报玩家 **离开** 或 **加入** 事件。     |
| broadcast_server | 布尔值 |    是否播报服务器 **开启** 或 **关闭** 事件。    |

### 运行服务

双击 `Start.bat` 运行服务器。当看到出现类似如下的日志时，

```log
05-25 19:49:08 [INFO] nonebot | OneBot V11 | Bot 2********6 connected
```

即代表机器人**连接成功**，你可以向群内发送`help`指令，若机器人正常回复，那么恭喜你已经安装成功了。若无反应，请检查配置是否正确，或联系作者寻求帮助。开始使用你的机器人吧！

> 若遇到问题，或有更好的想法，可以加入 QQ 群 `962802248` 向作者反馈。
