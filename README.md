# Minecraft_QQBot

**一款通过 MCDReforged 插件与 Minecraft 交互的 Python QQ 机器人**。功能丰富，使用简单可自行配置。目前已实现的功能有：

- 使用 !!qq 指令在游戏内向 QQ 群发送消息。
- 把 QQ 群内的消息转发到游戏内。
- 禁用 QQ 群内的特定命令。
- 对 QQ 群指令相应。目前已实现的指令有：
  - `luck` 查看今日幸运指数。
  - `list` 查询每个服务器的玩家在线情况。（依靠原版list指令实现）
  - `help` 查看帮助信息。
  - `server` 查看当前在线的服务器并显示对应编号。
  - `bound` 有关绑定白名单的指令。
  - `command` 运行指令到服务器。

更多功能还在探索中……

> [!CAUTION]
> **`Data` 文件夹下的 `Server.json` 文件是服务器数据文件，储存着 Minecraft 服务器信息，包括 Rcon 端口和密码等重要数据。请妥善保管此文件以免有心人利用入侵服务器。若有泄露，请立即修改 Rcon 密码并重新启动服务器！如若服务器因此被入侵造成的损失，作者概不负责。**

## 使用前准备

环境准备：Python

所需Python包：mcdreforged>=2.12.3 , nonebot2[fastapi]>=2.3.1及nonebot-adapter-onebot>=2.4.3

> [!WARNING]
> 此机器人仅支持 Python 3.8 及以上版本。若版本过低可能会出现不可预知的错误。

您可以在命令行内输入以下指令一键安装必要依赖：

```bash
pip3 install "nonebot2[fastapi]>=2.3.1", "nonebot-adapter-onebot>=2.4.3", "mcdreforged>=2.12.3"
```

此外，您可以自行选择是否安装其他依赖库，一些拓展的指令需要额外安装额外的依赖库，如果不安装仅会影响其对应的部分指令的使用，对其他指令没有影响。

- 如你需要使用 server status 指令，您需要安装 `matplotlib` 库。使用如下指令安装：

```bash
pip install matplotlib
```

## 配置环境

### 设置后端（以LLOneBot为例，此处仅提供对接方法）

请参照 [快速开始|LLOneBot](https://llonebot.github.io/zh-CN/guide/getting-started) 进行LLOneBot的安装

在安装完成后打开LLoneBot的设置界面，打开"启用反向WebShocket服务"，在其中添加一个监听地址

```bash
ws://127.0.0.1:8000/onebot/v11/
```

然后设置一个Access Token（也可以不设置）并点击保存

至此就已经完成了机器人后端的部署及设置

### 设置机器人服务端

解压在 Releases 中下载的 `BotServer.zip` 到任意位置，进入 `BotServer` 文件夹，编辑文件夹下的 [`.env`](https://github.com/Lonely-Sails/Minecraft_QQBot/blob/main/BotServer/.env) 文件

一般只需要对以下内容进行修改，未提到内容按照.env文件中的注释编辑即可

#### Bot超级用户（管理员）

```bash
SUPERUSERS=["2101596336"]
修改内容引号中内容为你的 QQ 账号，如需添加多个管理员请使用英文状态下的逗号进行分隔
并在新增的账号外添加英文双引号

例：SUPERUSERS=["123456","654321"]
```

#### 机器人连接密钥

```bash
ONEBOT_ACCESS_TOKEN=YourAccessToken
此处内容为您在LLOneBot等机器人后端处设置的连接密钥(Access Token)
如未进行设置请在 .env 文件中删除等号后面的内容

例：ONEBOT_ACCESS_TOKEN=
```

#### 与插件连接的密钥

```bash
TOKEN=YourToken
此处内容为应与插件的config文件中设置的Token内相同
建议对其进行修改（修改BotServer后不要忘记在MCDR插件的Config里同样进行修改）
```

#### 指令群

```bash
COMMAND_GROUPS=[1234567890]
请将括号中内容修改为您的 QQ 群号，此处设置的群号用于接收如"list","commmand"等指令的控制
如需添加多个聊群请在两群号中间添加一个英文逗号并在逗号后面添加一个空格
（一般与消息同步群相同即可）

例：COMMAND_GROUPS=[1234567890, 9876543210]
```

#### 消息同步群

```bash
SYNC_MESSAGE_GROUPS=[1234567890, 9876543210]
请将括号中内容修改为您的 QQ 群号，此项为同步至服务器及在游戏中使用'!!qq'指令后发送的聊群
```

#### 假人前缀

```bash
BOT_PREFIX=bot_
如果你的服务器添加了Carpet模组并开启了'/player'指令的使用权限
且使用了Carpet TIS拓展的'fakePlayerNamePrefix'功能，请在此处进行设置（如果进行了修改）

例：BOT_PREFIX=假的bot_
```

#### 播报玩家进退信息

```bash
BROADCAST_PLAYER=true
如果玩家数量众多或玩家频繁进出可能会导致消息同步群被玩家进退消息刷屏，请修改此项为false
```

### 运行机器人服务端

双击解压后的 `BotServer` 文件夹内的 `Start.bat` 运行机器人服务器。当看到出现类似如下的日志时，

```log
05-25 19:49:08 [INFO] nonebot | OneBot V11 | Bot 2********6 connected
```

即代表机器人**连接成功**，你可以向群内发送`help`指令，若机器人正常回复，那么恭喜你已经安装成功了，开始使用你的机器人吧！

若无反应，请检查配置是否正确，或联系作者寻求帮助。

> [!TIP]
> 请注意，若第一次启动机器人服务器，请确服务器启动然后再启动 Minecraft 服务器以保证机器人服务器能够连接到 Minecraft 服务器。

```bash
即第一次启动顺序为  ：LLOneBot等机器人后端 → BotServer → MCDR服务器
```

### 安装插件

将下载好的 `QQBot.mcdr` 文拷贝到 MCDR 的 插件文件夹 下，编辑 配置文件夹 `qq_bot` 下的 `config.json` 文件。配置文件内容参考如下：

```json
{
  "name": "服务器名称",
  "port": 8000,
  "token": "令牌",
  "sync_all_messages": false
}
```

其中各个字段的含义如下：

|      字段名       |  类型  |                       含义                       |
| :---------------: | :----: | :----------------------------------------------: |
|       port        |  整数  | 端口号，和服务器配置文件下的 PORT 保持一致即可。 |
|       name        | 字符串 |             服务器名称，中英文都可。             |
|       token       | 字符串 | 口令，和服务器配置文件下的 TOKEN 保持一致即可。  |
| sync_all_messages | 布尔值 |          是否转发游戏内玩家的所有消息。          |

当你看到类似 `发送服务器启动消息成功！` 的 Mcdr 日志时，你的 Mcdr 服务器已经成功连接到机器人服务器。若出现错误提示，请确保你的机器人服务器已经开启，或者配置文件的 Port 是否正确。你可以通过 `server` 指令查看服务器是否连接上机器人。

> [!WARNING]
> 如若你已确定你 Mcdr 插件的配置无误，但确仍没有显示对应的服务器已连接，请重启服务器后尝试！

## 鸣谢

感谢以下人员为此插件开发提供帮助，在此特别鸣谢：

- [meng877](https://github.com/meng877) 提出意见，贡献部分代码。
- [Decent_Kook](https://github.com/AISophon) 提供测试环境，提出意见。
- [creepebucket](https://github.com/creepebucket) 提供测试环境。

> [!TIP]
> 若遇到问题，或有更好的想法，可以加入 QQ 群 [`962802248`](https://qm.qq.com/q/B3kmvJl2xO) 或者提交 Issues 向作者反馈。
