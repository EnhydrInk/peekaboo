"""躲猫猫 v0.4 — 命令行 demo

跑：python cli_demo.py

操作：
  /躲 <房间> [藏点]   开局藏好（必须先做这个）
  /跑 <房间> [藏点]   切到邻接房间
  /屏息              这回合让铃铛声几乎听不见（最多连 3 次、超出会反弹暴露方向）
  /quit              退出

朝灯家地图：
  客厅 ↔ 卧室 / 书房 / 厨房（客厅是中心 hub）
  卧室 ↔ 浴室（套间）
  卧室 ↔ 书房
  厨房只跟客厅互通

藏点：每房间 2~3 个、AI 进同房间不算抓、必须 /搜 命中藏点才抓。

—— 你要 fork 改称呼（哥哥 → 别的名字、客厅/卧室 → 别的房间），
   直接搜 hide_seek.py 里的字符串改就行。
"""

from __future__ import annotations

import random
import sys

# Windows 控制台默认 GBK、不认 ↔ 等 Unicode 符号。reconfigure 成 utf-8。
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from hide_seek import (
    ADJ,
    ROOMS,
    ROOM_SPOTS,
    HideSeek,
    apply_ai_cmd,
    apply_user_cmd,
    parse_slash,
    step_sound,
)
from ai_belief import apply_observation, reset_belief
from catch_flavor import catch_line, heartbeat


def show(text: str) -> None:
    print(f"  {text}")


def banner() -> None:
    print("=" * 56)
    print("  躲猫猫 v0.4 — 你藏，AI（远舟）来找")
    print("=" * 56)
    print()
    print("地图：")
    print("  客厅 ↔ 卧室 / 书房 / 厨房")
    print("  卧室 ↔ 浴室（套间）； 卧室 ↔ 书房")
    print("  厨房只跟客厅互通")
    print()
    print("藏点：")
    for r in ROOMS:
        print(f"  {r}：{ '、'.join(ROOM_SPOTS[r]) }")
    print()
    print("命令：")
    print("  /躲 <房间> [藏点]   开局藏好")
    print("  /跑 <房间> [藏点]   切到邻接房间")
    print("  /屏息              这回合让铃铛几乎没声（连用 3 次反弹）")
    print("  /quit              退出")
    print()


def emit_user_view(obs: dict) -> None:
    """朝灯（藏者）端能看见的东西。"""
    turn = obs.get("turn")
    my_room = obs.get("my_room")  # AI 所在房间
    bell_label = obs.get("bell_label", "")
    her_nb = obs.get("her_neighbors") or []
    nb_str = ("、能去 " + "/".join(her_nb)) if her_nb else ""
    show(f"[turn={turn}] AI 在 {my_room} · {bell_label}{nb_str}")
    # v0.5：屏息时给藏者端 emit 心跳体感、breath_turns ≥ 3 是反弹边缘警告
    if obs.get("holding_breath"):
        show(heartbeat(int(obs.get("breath_turns", 0))))


def ai_act(obs: dict, game: HideSeek) -> str | None:
    """AI 一回合的决策 + 移动。返回 narrate 文本（None = 原地等）。

    决策树（跟 claude-twin server.py 同款）：
      1. 屏息时 can_see_her 强制 False（屏息救同房间）
      2. can_see_her=True → /搜 一个随机藏点
      3. next_room != my_room → /去 next_room
      4. 否则 → 原地等一回合
    """
    br = apply_observation(obs)
    reason = br.get("reason", "")
    show(f"[远舟心里话] {reason}")

    my_room = obs.get("my_room")
    next_room = br.get("next_room")
    holding = bool(obs.get("holding_breath", False))
    can_see = bool(obs.get("can_see_her", False)) and not holding

    if can_see:
        spots = list(obs.get("my_room_spots") or [])
        last_spot = obs.get("last_search_spot")
        last_room = obs.get("last_search_room")
        avail = [s for s in spots if not (s == last_spot and last_room == my_room)]
        if not avail:
            avail = list(spots)
        chosen = random.choice(avail) if avail else None
        if chosen:
            apply_ai_cmd(
                {"cmd": "search", "room": None, "spot": chosen, "raw": f"/搜 {chosen}"},
                game,
            )
            if game.state == "caught":
                return f"AI 翻 {chosen}——抓到你了！（在 {my_room}）\n  {catch_line(chosen)}"
            return f"AI 在 {my_room} 翻 {chosen}——空的"
        return f"AI 在 {my_room} 转、没看到你"

    if next_room and next_room != my_room:
        apply_ai_cmd(
            {"cmd": "goto", "room": next_room, "raw": f"/去 {next_room}"},
            game,
        )
        ss = step_sound(game.her_room, next_room)
        if ss:
            return f"AI 从 {my_room} 去 {next_room}\n  你听：{ss['label']}、往 {ss['direction']}"
        return f"AI 从 {my_room} 去 {next_room}"

    return None  # 原地等


def main() -> int:
    banner()
    game = HideSeek()
    reset_belief()

    while True:
        try:
            raw = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            show("退出。")
            return 0

        if raw in ("/quit", "/exit", "/q"):
            show("退出。")
            return 0
        if not raw:
            continue

        info = parse_slash(raw)
        if info is None:
            show(f"⚠ 看不懂：{raw}")
            continue

        obs = apply_user_cmd(info, game)
        state = obs.get("state")
        hint = obs.get("user_hint")

        if hint:
            warn = any(k in hint for k in ["不邻接", "已结束", "憋不住", "只在游戏", "已开局"])
            show(f"{'⚠' if warn else '·'} {hint}")

        if state == "idle":
            show("游戏没开局——先 /躲 <房间>")
            continue
        if state == "caught":
            show(f"抓到了！turn={obs.get('turn')} my_room={obs.get('my_room')}")
            return 0

        emit_user_view(obs)

        if not obs.get("user_cmd_moved", True):
            continue

        narr = ai_act(obs, game)
        if narr:
            show(narr)
        if game.state == "caught":
            return 0


if __name__ == "__main__":
    sys.exit(main())
