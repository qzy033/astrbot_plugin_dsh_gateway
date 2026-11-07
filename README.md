<div align="center">

# astrbot_plugin_dsh_gateway

_✨ 大肥鱼桥 · AstrBot 侧 ✨_

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%20~%204.29-orange.svg)](https://github.com/AstrBotDevs/AstrBot)
[![Version](https://img.shields.io/badge/version-0.7.0-blue)](CHANGELOG.md)
[![Repo](https://img.shields.io/badge/%E4%BB%93%E5%BA%93-astrbot__plugin__dsh__gateway-blue)](https://github.com/qzy033/astrbot_plugin_dsh_gateway)
[![DSH 侧](https://img.shields.io/badge/%E9%85%8D%E5%A5%97-DSH%20%E4%BE%A7%E4%BB%93%E5%BA%93-blueviolet)](https://github.com/qzy033/dsh-astrbot-gateway)

</div>

---

## 🤝 介绍

让本地 AI 智能体（dsh / DeepSeek Harness 这类）借你的 AstrBot 通道，把消息讲给你听。

智能体说的话不会直发到你的聊天窗口，而是先送到这一侧的**唯一闸门**：消息落盘后，插件立刻排一个一次性任务把 AstrBot 里那个助手角色叫醒，由它自己读中转件、用自己的话讲给你听，讲完归档。哪句话是给智能体的、哪句是闲聊，也由这一侧判断。

- 🔒 智能体拿不到你的账号，只能调本机 HTTP 接口
- ⚡ 收到消息三秒内叫醒助手，由助手本人开口；叫不动才回退到即时总结直发
- 🧠 助手说话时带着自己的人设和记忆，不是插件拿模板替你转述
- 🧩 只装这一侧也能跑，安安静静待着，不报错也不刷屏
- 🔗 与 dsh 侧插件 `dsh-astrbot-gateway` 配对使用，两侧各装各的
- 🚇 自带直通模式：私聊发 `dsh/1` 就能绕过总结，原文进出
- 🧩 兼容 AstrBot 4.0 – 4.29；主动发送走 `StarTools.send_message(umo)`，不再依赖 4.26 已删除的旧接口

## 🗂️ 两个仓库的关系

这个项目有两半，分别住在两个仓库里，不是 fork、也不是子模块：

| 仓库 | 放什么 | 装到哪 |
| --- | --- | --- |
| **本仓库** `astrbot_plugin_dsh_gateway` | AstrBot 侧插件本体（根目录就是插件） | AstrBot 面板 → 插件管理 |
| 配套仓库 [`dsh-astrbot-gateway`](https://github.com/qzy033/dsh-astrbot-gateway) | DSH 侧插件（npm 包）+ 全部文档 + 安装工具 | DSH 的 profile |

两边只通过同一个桥接目录（`cache/`）和本机 HTTP 接口对接，**谁先装、谁后装都不会报错**。
完整安装手册在配套仓库的 [`docs/install.md`](https://github.com/qzy033/dsh-astrbot-gateway/blob/main/docs/install.md)。

## 📦 安装

**方式一：从仓库一键装（现在就能用）**

AstrBot 面板 → 插件管理 → 安装插件 → 仓库地址填本仓库地址：

```
https://github.com/qzy033/astrbot_plugin_dsh_gateway
```

本仓库根目录就是插件本体（`metadata.yaml`、`main.py`、`_conf_schema.json` 直接放在根下），
所以填干净地址即可，**不要带 `/tree/...` 后缀**。装完 AstrBot 会按 `metadata.yaml` 里的 `name` 把目录改名成
`astrbot_plugin_dsh_gateway`。

**方式二：插件市场**

等本插件通过市场收录后，可以直接在 AstrBot 插件市场搜索 `astrbot_plugin_dsh_gateway`，点击安装并启用。
市场里暂时还搜不到就用方式一，装的是同一个仓库的同一份代码。

**方式三：手动**

把本目录放进 `AstrBot 数据目录/plugins/` 下，或者在面板的插件管理里上传本目录打成的 zip，然后按下面的「装完三步走」配置。

**装完三步走**

1. 打开插件配置，填「转达目标账号」：私聊填 QQ 号，群聊填群号。
2. 「桥接项目目录」可以留空，留空就用 `用户主目录/dsh-astrbot-gateway`；如果 dsh 侧已经指定过目录，这里填同一个就行。
3. 重载或重启 AstrBot 让配置生效，然后在本机浏览器打开下面这个地址自检：

```
http://127.0.0.1:6185/api/plug/astrbot_plugin_dsh_gateway/ping
```

看到 `pong` 就说明通道通了。端口以你 Dashboard 的实际端口为准，插件日志里也会直接打出这个自检地址。

> 还没装 dsh 侧插件也没关系：这一侧就是个安静的本机接口，装上不会报错，等 dsh 那侧装好自己就会接上。

## ⚙️ 配置

面板路径：插件管理 → astrbot_plugin_dsh_gateway → 操作 → 插件配置。

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| project_dir | 桥接项目目录，缓存区 cache/ 就在它下面，dsh 侧要填同一个 | 用户主目录/dsh-astrbot-gateway |
| target_id | 转达目标账号，私聊填 QQ 号，群聊填群号 | 空 |
| target_type | PrivateMessage 私聊 / GroupMessage 群聊 | PrivateMessage |
| platform | 平台适配器 ID | aiocqhttp |
| wake_gatekeeper | 叫醒闸门，由助手自己开口转达 | 开 |
| wake_delay_seconds | 落盘后隔几秒叫醒助手，建议 2 到 5 | 3 |
| umo_platform | 会话串里的平台实例 id，留空自动解析 | 空 |
| instant_summary | 叫醒失败时的兜底：即时总结直发 | 开 |
| tag | 转达内容前的小标签 | [dsh] |
| memory_dir | 事件流水目录 | AstrBot 插件数据目录 |
| source_label | 中转记录里的来源标记 | dsh |
| relay_dir_name | 中转箱目录名 | dsh_relay |
| relay_done_dir_name | 已转达子目录名 | done |
| events_file_name | 事件流水文件名 | relay_events.jsonl |
| access_file_name | 自签令牌写入的文件名，两侧要一致 | bridge_access.json |
| summary_prompt | 总结用的系统提示词 | 留空用内置通用版 |
| direct_enter_cmd | 进直通的私聊指令 | dsh/1 |
| direct_exit_cmd | 退直通的私聊指令 | dsh/0 |
| direct_new_cmd | 直通里换一条新会话的指令 | dsh/2 |
| direct_echo | 每条投递回一句「已直送」收执 | 关 |

## 🚇 直通模式（主人自己开的旁路）

平时主人的每句话先到闸门手里筛一遍，dsh 的回话也先落中转箱、再由闸门转述。要连着跟 dsh 来回聊的时候，主人可以在私聊里把这道闸门暂时撤掉：

- `dsh/1` 进直通：之后主人发的话原文写成 `cache/inbox` 指令投给 dsh，dsh 的回话原文直接推回主人，不叫醒闸门、不做总结。
- `dsh/0` 退直通：回到原来的闸门模式。
- `dsh/2` 换会话：直通还开着，但下一条起换一条全新的 dsh 会话，不接上一段上下文。

三条指令只在私聊里认、也只认配置里那个 `target_id`；插件抢在默认对话处理之前把事件拦下，指令本身不落进对话，也不会被当成任务投给 dsh。开关状态写在 `cache/direct_state.json`（`on` 字段），重启也认得。直通里每条投递在 `relay_events.jsonl` 留一条 `master-direct`，每条回话留一条 `dsh-direct`，查账看这两类就够。

注意事项：

- 直通期间闸门是闭嘴的：人家不替主人把关，也不会自己接下一步；要想让人接手，先发 `dsh/0`。
- 直通是给「连续来回」用的，不是默认状态：不开的时候一句都不会绕过闸门。
- DSH 侧要 0.7.0 及以上才认 `newSession`（`dsh/1`、`dsh/2` 后的第一条会带上它）；旧版 DSH 插件只会接着上一条会话跑，功能仍可用，只是 `dsh/2` 换不了新会话。
- dsh 侧仍受它自己的审批与权限策略管，会话停在等审批那步只能在 DSH 界面点。
- 新会话要有可用的模型路由：宿主没配到能用的 provider 时投喂会失败，日志里会写明原因。
- 两个插件改完的生效方式不同：dsh 侧必须重启 dsh（bundle 插件 + ESM 缓存），AstrBot 侧重载插件即可。

## ⌨️ 使用说明

基址：`http://127.0.0.1:6185/api/plug/astrbot_plugin_dsh_gateway`

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| /ping | GET | 健康检查，返回 pong |
| /send | POST | 把消息交给闸门，闸门被叫醒后自己转达 |
| /relay | GET | 查看中转箱里还没转达出去的消息 |

### POST /send

请求头：`Authorization: Bearer <token>`，令牌在访问文件里，不用自己配。

```json
{
  "text": "要发送的文本",
  "target": "收件账号，可省略",
  "type": "PrivateMessage",
  "direct": false
}
```

- `text` 必填；`target` 与 `type` 省略时用插件配置里的默认值。
- 接口本身不等模型，落盘即秒回；插件随后排一个一次性任务把助手叫醒，由它自己开口。
- `"direct": true` 会绕过闸门直发，默认没人该用它。

```bash
curl -X POST http://127.0.0.1:6185/api/plug/astrbot_plugin_dsh_gateway/send ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <token>" ^
  -d "{\"text\":\"[dsh] 任务完成啦\"}"
```

## 🔍 排查

| 现象 | 大概原因和做法 |
| --- | --- |
| 打开 ping 显示「未找到该路由」 | 插件没启用，或者插件目录改过名。去面板确认插件是启用状态，重载一次 |
| send 返回 401 或 403 | 令牌过期或 Dashboard 密钥改过。重载本插件，让它重新签发访问文件 |
| 消息只落中转箱，没转达 | 「转达目标账号」没填。填上再重载 |
| 日志里写 Invalid session | 会话串的消息类型不对。0.6.0 已内置换算，若还出现请重载插件 |
| 日志里写 cannot find platform for session | 平台那一栏被填成了平台实例 id。填适配器名，或把实例 id 写进 umo_platform |
| 日志里没有自检地址 | 没读到 dashboard.jwt_secret。确认面板密码配置在，重载插件 |
| 日志里写 `has no attribute 'send_message_by_id'` | AstrBot 4.26+ 已删除旧接口。升到本插件 0.7.0，它改走 `StarTools.send_message(umo)` |
| 日志里写「宿主没找到匹配的平台」 | 平台名没对上：`platform` 填适配器名（如 `aiocqhttp`）；实例 id 不一样就写进 `umo_platform` |
| 直通发了没反应 | 先确认 DSH 侧在跑；再看 `cache/inbox/` 有没有新文件、DSH 日志里 `[dsh-gateway]` 那几行 |
| 想让智能体直发用户 | 不建议。真要救火就用 `direct: true` |

## 🧱 实现方式

AstrBot 的开放接口 `/api/v1/*` 需要 API Key，插件自带的 `/api/plug/*` 又受 Dashboard 登录鉴权保护。
本插件在加载时用 Dashboard 的 `jwt_secret` 自签一枚长期令牌，写进约定的访问文件：

1. `AstrBot 数据目录/bridge_access.json`
2. `桥接项目目录/cache/bridge_access.json`

dsh 侧只读第二份，带上令牌就能调接口。改过 Dashboard 密钥后，重载本插件即可刷新。

转达不走插件的模型调用，而是用 AstrBot 自带的定时任务管理器排一个 `active_agent` 一次性任务：
到点由框架把助手那个会话叫醒，唤醒词里写明读哪个中转文件、讲给谁、讲完归档。
助手是自己那一轮的说话人，插件全程不代替它发言。

主动发消息用的是 `StarTools.send_message(umo, chain)`：

```python
umo = f"{平台实例id}:{FriendMessage|GroupMessage}:{目标id}"
await StarTools.send_message(umo, MessageChain([Plain(text)]))
```

`send_message` 从 AstrBot 4.0 到 4.29 一直都在；4.26 删掉的是旧的
`send_message_by_id`，本插件 0.7.0 起不再引用它。

## 🧪 自测

不依赖真的 AstrBot 安装，直接用假模块把 `main.py` 导进来验证：

```bash
python tests/test_send_compat.py
```

覆盖 6 件事：umo 拼装（私聊/群聊/临时目标）、走的是 `StarTools.send_message`、
宿主返回 `False` 时按失败处理、没填目标时不发送、代码里没有旧接口调用。
AstrBot 4.28.2 的真运行时冒烟另做：`python -c "import ..."` 能 import 且能正常注册路由。

## 📄 许可

MIT，详见仓库的 LICENSE。

## 📝 更新日志

见 [CHANGELOG.md](CHANGELOG.md)。
