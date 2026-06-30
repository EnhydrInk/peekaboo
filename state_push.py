"""peekaboo state push — 把游戏 state 推给外部观察端（如 InKieran iOS Fugue tab）。

env var `PEEKABOO_PUSH_URL` 指向 POST endpoint（如 https://kieran.enhydrink.com/api/fugue/event）。
没设 = 不 push（纯 CLI 模式、保持 peekaboo 零耦合）。

零依赖、用 stdlib urllib。push 失败静默忽略——不阻塞游戏。
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def push(payload: dict[str, Any], timeout: float = 1.0) -> None:
    """非阻塞 push。url 没设 / 网络挂了 都静默忽略。"""
    url = os.environ.get("PEEKABOO_PUSH_URL")
    if not url:
        return
    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=timeout)
    except (urllib.error.URLError, OSError, TimeoutError):
        pass


def snapshot(game: Any, breath_uses_total: int, last_emit: str = "") -> dict:
    """从 HideSeek game state 拆出 push payload。"""
    return {
        "playing": getattr(game, "state", "idle") == "running",
        "state": getattr(game, "state", "idle"),
        "turn": getattr(game, "turn", 0),
        "your_room": getattr(game, "her_room", None),
        "your_spot": getattr(game, "her_spot", None),
        "ai_room": getattr(game, "my_room", None),
        "holding_breath": getattr(game, "holding_breath", False),
        "breath_turns": getattr(game, "breath_turns", 0),
        "breath_uses_total": breath_uses_total,
        "last_emit": last_emit,
    }
