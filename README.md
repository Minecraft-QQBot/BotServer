# Minecraft_QQBot

**一款基于 Nonebot2 用多种方式与 Minecraft 交互的 Python QQ 机器人**。功能丰富，使用简单且可以自行配置，仅需简单配置即可使用。目前已实现的功能有：

- 多服互联。
- 可使用指令在游戏内向 QQ 群发送消息。
- 把 QQ 群内的消息转发到游戏内。
- 禁用 QQ 群内的特定命令。
- 对 QQ 群指令相应。目前已实现的指令有：
  - `luck` 查看今日幸运指数。
  - `list` 查询每个服务器的玩家在线情况。（依靠原版 list 指令实现）
  - `help` 查看帮助信息。
  - `server` 查看当前在线的服务器并显示对应编号。
  - `bound` 有关绑定白名单的指令。
  - `command` 发送指令到服务器。

更多功能还在探索中……

> [!CAUTION]
> **`Data` 文件夹下的 `Server.json` 文件是服务器数据文件，储存着 Minecraft 服务器信息，包括 Rcon 端口和密码等重要数据。请妥善保管此文件以免有心人利用入侵服务器。若有泄露，请立即修改 Rcon 密码并重新启动服务器！如若服务器因此被入侵造成的损失，本作者概不负责。**

## 安装插件

本机器人可通过各种方式与 Minecraft 服务器进行交互，包括：

- [Bukkit](https://www.github.com/Minecraft-QQBot/Bukkit) 插件（此插件由于开发者不开源，暂不提供）
- [McdReforged](https://www.github.com/Minecraft-QQBot/McdReforged) 插件

请前往你需要插件的仓库按照说明进行安装。

## 安装依赖

在命令行内输入以下指令安装依赖：

```bash
pip3 install "nonebot2[fastapi]>=2.3.1", "nonebot-adapter-onebot>=2.4.3", "mcdreforged>=2.12.3"
```

以上是运行本机器所必须的。此外，您可以自行选择是否安装其他依赖库，一些拓展的指令需要额外安装。不安装也仅会影响那部分指令的使用。

如若你需要使用 server status 指令，您需安装 `matplotlib` 库。使用如下指令安装：

```bash
pip3 install matplotlib
```

> [!WARNING]
> 此机器人仅支持 Python 3.8 及以上版本。若版本过低，否则可能会出现不可预知的错误。

### 配置环境

你可以到 [Releases](https://github.com/Minecraft-QQBot/BotServer/releases) 下载最新版本的机器人服务器。

解压下载的 `BotServer.zip` 到任意位置，进入 `BotServer` 文件夹，编辑文件夹下的 [`.env`](https://github.com/Minecraft-QQBot/BotServer/blob/main/BotServer/.env) 文件，按照注释配置即可。

对于 QQ 机器人（如 GoCqHttp，LLOneBot，NapCat 等）的配置请见 [Onebot](https://onebot.adapters.nonebot.dev/docs/guide/setup)
适配器文档。

> 本机器人仅支持 Onebot V11 协议，建议用 Websocket 反向链接。

### 运行服务

双击解压后的 `BotServer` 文件夹内的 `Start.bat` 运行机器人服务器。当看到出现类似如下的日志时，

```log
05-25 19:49:08 [INFO] nonebot | OneBot V11 | Bot 2********6 connected
```

即代表机器人**连接成功**，你可以向群内发送`help`指令，若机器人正常回复，那么恭喜你已经安装成功了。若无反应，请检查配置是否正确，或联系作者寻求帮助。开始使用你的机器人吧！

> [!TIP]
> 请注意，若第一次启动机器人，请确机器人启动然后再启动 Minecraft 服务器，以保证机器人能够连接到 Minecraft 服务器。

## 帮助

Q: 如何使用指令？

A: 你可以在 QQ 群内发送 `help` 指令查看机器人的帮助信息，也可以用 `help <指令名称>` 查看具体指令的帮助信息。

## 鸣谢

感谢以下人员为此机器人开发提供帮助，在此特别鸣谢：

- []
- [meng877](https://github.com/meng877) 提出意见，贡献部分代码。
- [Decent_Kook](https://github.com/AISophon) 提供测试环境，提出意见。
- [creepebucket](https://github.com/creepebucket) 提供测试环境。

> [!TIP]
> 若遇到问题，或有更好的想法，可以加入 QQ 群 [`962802248`](https://qm.qq.com/q/B3kmvJl2xO) 或者提交 Issues 向作者反馈。若你有能力，欢迎为本项目提供代码贡献！

## 友链

- TQM 服务器
- [LemonFate 服务器](https://www.lemonfate.cn/)
- [RedstoneDaily 红石日报](https://www.redstonedaily.com/)
