# WebSocket 通信格式

以下所有涉及字典的传输格式均采用 `JSON` 格式，并且经过 `Base64` 编码。对于服务器或客户端的回应，也应转换为 `JSON`
后经过 `Base64` 解码。

## 验证身份

在 WebSocket 的 Headers 内加入以下参数验证身份：

|  参数名   |                     值                     |
|:------:|:-----------------------------------------:|
| `type` | 客户端类型，当前有 `Fabric` `McdReforged` `Spigot` |
| `info` |    一个字典，包含 `token` 机器人密钥和 `name` 服务器名称    |

## 监听机器人

> ws://{host}:{port}/websocket/minecraft

在与机器人建立连接后，循环监听机器人发送的消息，并解析。

机器人发送的消息格式为：

```json
{
  "type": "message",
  "data": "SomethingData"
}
```

其中 `type` 为消息类型，`data` 为消息数据。请注意，`data` 根据具体情况可能为字符类型或是为空。

## 发送事件

> ws://{host}:{port}/websocket/bot

在建立连接后，发送事件给机器人，如玩家进出游戏等。基本格式如下：

```json
{
  "type": "event_name",
  "data": "SomethingData"
}
```

其中，`type` 为事件类型，`data` 为事件数据。请注意，`data` 根据具体情况可能为字符类型或是为空。

具体事件名称如下：

|       事件名称        |   描述   |          携带数据          |
|:-----------------:|:------:|:----------------------:|
|     `message`     | 发送群消息  |         发送的消息          |
| `server_startup`  | 服务器启动  |           无            |
| `server_shutdown` | 服务器关闭  |           无            |
|  `player_joined`  | 玩家进入游戏 |         玩家的名字          |
|   `player_left`   | 玩家离开游戏 |         玩家的名字          |
|  `player_death`   |  玩家死亡  | 一个列表，第一项为玩家名字，第二项为死亡原因 |
|   `player_chat`   |  玩家聊天  | 一个列表，第一项为玩家名字，第二项为聊天内容 |

服务器返回的格式为：

```json
{
  "success": true
}
```

字面意思，即发送事件是否成功。
