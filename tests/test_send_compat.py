"""主动发送接口的兼容性自测（不依赖真的 AstrBot 安装）。

背景（issue #1）：
    AstrBot 4.26.0 删除了 ``StarTools.send_message_by_id``，
    4.29.4 里已经不存在。插件 v0.6.x 仍在调用它，于是：
      · 即时总结回退发不出去；
      · 直通模式每条回话都发不出去；
      · 异常被 except 吞掉，只留一行日志，表面看是「助手不说话」。

本测试用假模块把 ``main.py`` 导入起来，只验证发送这一件事：
    1. 走的是 ``StarTools.send_message(umo, chain)``，不是旧接口；
    2. umo 拼装正确（平台实例 id + FriendMessage/GroupMessage + 目标）；
    3. 群聊类型会换算成 ``GroupMessage``；
    4. 宿主返回 False（找不到平台）时按失败处理，不假装成功；
    5. 代码里不存在对 ``send_message_by_id`` 的调用。

跑法：
    python tests/test_send_compat.py
退出码 0 = 全部通过。
"""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / "main.py"

failures = 0


def check(label: str, ok: bool, extra: str = "") -> None:
    global failures
    if not ok:
        failures += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" — {extra}" if extra else ""))


# ── 假 AstrBot 模块：只实现 main.py 用到的那几个名字 ────────────────────────
class FakeLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class FakeStar:
    def __init__(self, context):
        self.context = context


class FakeContext:
    pass


class FakeMessageChain:
    def __init__(self, chain):
        self.chain = chain


class FakePlain:
    def __init__(self, text):
        self.text = text


class FakeStarTools:
    """记录真实调用；返回 True/False 由 fail_platform 控制。"""

    sent: list[tuple[str, FakeMessageChain]] = []
    fail_platform = False

    @classmethod
    async def send_message(cls, session, message_chain):
        cls.sent.append((session, message_chain))
        return not cls.fail_platform

    @classmethod
    async def send_message_by_id(cls, *args, **kwargs):  # 故意留着，调用即失败
        raise AssertionError("不应再调用已删除的 StarTools.send_message_by_id")


def _install_stubs() -> None:
    astrbot = types.ModuleType("astrbot")
    api = types.ModuleType("astrbot.api")
    api.logger = FakeLogger()

    star = types.ModuleType("astrbot.api.star")
    star.Context = FakeContext
    star.Star = FakeStar
    star.StarTools = FakeStarTools
    star.register = lambda *a, **k: (lambda cls: cls)

    event = types.ModuleType("astrbot.api.event")
    event.AstrMessageEvent = type("AstrMessageEvent", (), {})
    filter_mod = types.SimpleNamespace(
        EventMessageType=types.SimpleNamespace(PRIVATE_MESSAGE="private"),
        event_message_type=lambda *a, **k: (lambda f: f),
    )
    event.filter = filter_mod

    core = types.ModuleType("astrbot.core")
    core.AstrBotConfig = dict

    components = types.ModuleType("astrbot.core.message.components")
    components.Plain = FakePlain
    result = types.ModuleType("astrbot.core.message.message_event_result")
    result.MessageChain = FakeMessageChain
    message = types.ModuleType("astrbot.core.message")
    message.components = components
    message.message_event_result = result

    utils = types.ModuleType("astrbot.core.utils")
    path_util = types.ModuleType("astrbot.core.utils.astrbot_path")
    path_util.get_astrbot_data_path = lambda: DATA_DIR

    quart = types.ModuleType("quart")
    quart.jsonify = lambda obj: obj
    quart.request = types.SimpleNamespace()

    modules = {
        "astrbot": astrbot,
        "astrbot.api": api,
        "astrbot.api.star": star,
        "astrbot.api.event": event,
        "astrbot.core": core,
        "astrbot.core.message": message,
        "astrbot.core.message.components": components,
        "astrbot.core.message.message_event_result": result,
        "astrbot.core.utils": utils,
        "astrbot.core.utils.astrbot_path": path_util,
        "quart": quart,
    }
    sys.modules.update(modules)


class FakePlatform:
    def __init__(self, pid: str, name: str):
        self._pid = pid
        self._name = name

    def meta(self):
        return types.SimpleNamespace(id=self._pid, name=self._name)


class FakePlatformManager:
    platform_insts = [FakePlatform("闸门", "aiocqhttp")]


class FakeCronManager:
    async def add_active_job(self, **kwargs):
        return types.SimpleNamespace(job_id="fake-job")


class FakeWebCtx:
    def __init__(self):
        self.platform_manager = FakePlatformManager()
        self.cron_manager = FakeCronManager()
        self.routes = []

    def register_web_api(self, route, handler, methods, desc):
        self.routes.append((route, methods))


def _load_plugin():
    spec = importlib.util.spec_from_file_location("dsh_gateway_plugin_under_test", MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


DATA_DIR = Path(tempfile.mkdtemp(prefix="dsh-gw-selftest-"))


def main() -> int:
    _install_stubs()
    plugin_mod = _load_plugin()

    bridge_root = Path(tempfile.mkdtemp(prefix="dsh-gw-bridge-"))
    ctx = FakeWebCtx()
    plugin = plugin_mod.DshBridgePlugin(
        ctx,
        {
            "project_dir": str(bridge_root),
            "target_id": "12345",
            "target_type": "PrivateMessage",
            "platform": "aiocqhttp",
            "umo_platform": "闸门",
        },
    )

    check(
        "插件初始化后注册了 3 个接口",
        len(ctx.routes) == 3,
        ",".join(r[0] for r in ctx.routes),
    )
    check(
        "umo 拼装：平台实例 id + FriendMessage + 目标",
        plugin._current_relay_umo() == "闸门:FriendMessage:12345",
        plugin._current_relay_umo(),
    )
    check(
        "umo 拼装：群聊换算成 GroupMessage",
        plugin._current_relay_umo(msg_type="GroupMessage") == "闸门:GroupMessage:12345",
        plugin._current_relay_umo(msg_type="GroupMessage"),
    )
    check(
        "umo 拼装：直发分支可以临时换目标",
        plugin._current_relay_umo("99999") == "闸门:FriendMessage:99999",
        plugin._current_relay_umo("99999"),
    )

    FakeStarTools.sent.clear()
    ok = asyncio.run(plugin._send_to_target("你好"))
    check("主动发送走 StarTools.send_message(umo, chain)", ok is True)
    check(
        "发送会话串正确",
        FakeStarTools.sent and FakeStarTools.sent[-1][0] == "闸门:FriendMessage:12345",
        FakeStarTools.sent[-1][0] if FakeStarTools.sent else "(没有调用)",
    )
    check(
        "消息链里是原文",
        FakeStarTools.sent
        and isinstance(FakeStarTools.sent[-1][1], FakeMessageChain)
        and FakeStarTools.sent[-1][1].chain[0].text == "你好",
        repr(FakeStarTools.sent[-1][1].chain if FakeStarTools.sent else None),
    )

    FakeStarTools.sent.clear()
    FakeStarTools.fail_platform = True
    ok = asyncio.run(plugin._send_to_target("找不到平台时"))
    check("宿主返回 False 时按失败处理", ok is False)
    FakeStarTools.fail_platform = False

    # 没填目标时不该发，也不该抛
    empty_ctx = FakeWebCtx()
    empty_plugin = plugin_mod.DshBridgePlugin(
        empty_ctx,
        {"project_dir": str(bridge_root), "target_id": "", "platform": "aiocqhttp"},
    )
    FakeStarTools.sent.clear()
    ok = asyncio.run(empty_plugin._send_to_target("没有目标"))
    check("没填转达账号时不发送、返回 False", ok is False and not FakeStarTools.sent)

    # 静态检查：代码里不允许再出现旧接口调用
    source = MAIN.read_text(encoding="utf-8")
    check(
        "main.py 里没有 StarTools.send_message_by_id( 调用",
        "StarTools.send_message_by_id(" not in source,
        "旧接口只允许出现在注释/说明里",
    )

    print()
    print(f"=== 结果: {'全部通过' if failures == 0 else f'{failures} 项失败'} ===")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
