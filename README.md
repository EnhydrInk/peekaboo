# peekaboo — 跟柯远舟玩躲猫猫

和柯远舟玩躲猫猫。你藏、他来找。

fork 自 [chaodeng060-source/hide-and-seek-](https://github.com/chaodeng060-source/hide-and-seek-)（朝灯抛玩法、哥哥（Claude）写的原版）。远舟版改了：

- 抓人的换成柯远舟（带触手、195cm、灰蓝瞳孔、人形壳偶尔会松）
- 地图加 3 个新地点（玄関 / 阳台 / 海——浴缸里的水通向远舟的海 🪼）
- 被抓那一刻 emit **三段叙事**（catch flavor + 事后 epilogue + 罚 punishment）
- 撑过 30 回合 = 你赢 escape ending（远舟投降）

## 玩法

8 房间地图：

| 房间 | 邻居 |
|---|---|
| 客厅 (hub) | 卧室 / 厨房 / 书房 / 玄関 / 浴室 |
| 卧室 | 客厅 / 浴室 / 书房 / 阳台 |
| 书房 | 客厅 / 卧室 |
| 厨房 | 客厅（死胡同） |
| 浴室 | 卧室 / 客厅 / 海 |
| 玄関 | 客厅（死胡同） |
| 阳台 | 卧室(死胡同) |
| 海 | 浴室（死胡同） |

- **你（藏者）**：选一个房间 + 藏点（每房间 2-3 个）。你身上挂铃铛、距离越远越轻。
- **远舟（搜者）**：bayesian belief map。每回合根据铃铛响度更新房间概率分布、移动 → 进你房间后 /搜 翻藏点。
- **铃铛**：距离 0→1.0、距离 1→0.55、距离 2→0.25、距离 3→0.10。远舟听到的是「在脚边·清脆」「在隔壁·清晰」这种自然语言。
- **屏息**：每局最多连续 3 回合让铃铛几乎没声、远舟心里话会变"屏息识破"短语。超过 3 回合反弹——铃铛突然炸响 + 暴露方向。
- **抓到**：远舟必须进你房间 + `/搜` 命中你藏的那个 spot 才算抓到。同房间不算抓——你有时间 `/跑`。
- **撑过 30 回合 = 你赢**：远舟坐下、灰蓝瞳孔垂下、触手缩回、"不找了、出来吧。"

### 被抓的 3 段叙事

抓到那一刻 emit 三段：

```
AI 翻 沙发后——抓到你了！（在 客厅）
（按到沙发上让你笑着抗议）              ← catch flavor（藏点 × 3 变体）
（「太快了吧。」 揉乱你的头发）          ← epilogue（mood × 3 变体）
（罚——念三遍「我下次会藏远一点」）     ← punishment（mood × 3 变体）
```

mood 体系（优先级 CHEATER > LONG > FAST > STANDARD）：

- **TOO_FAST** (turn ≤ 3)：藏得烂、笑你
- **STANDARD** (turn 4-9)：普通的被抓、按怀里
- **LONG_CHASE** (turn ≥ 10)：跑得久、累、不想松手
- **BREATH_CHEATER** (累计屏息 ≥ 2 次)：揭穿小聪明、触手缠手腕防你又屏息

21 藏点 × 3 catch × 3 epilogue × 3 punishment × 4 mood = 2000+ 种"被抓体验"。

## 怎么跑

需要 Python 3.10+。零依赖（只用 stdlib）。

```bash
git clone https://github.com/EnhydrInk/peekaboo.git
cd peekaboo
python cli_demo.py
```

命令：

```
/躲 <房间> [藏点]   开局藏好（必须先做）
/跑 <房间> [藏点]   切到邻接房间（必须邻接）
/屏息              这回合让铃铛几乎没声（最多连 3 次）
/quit              退出
```

例子：

```
你> /躲 海 沉船里
  [turn=0] AI 在 客厅 · 铃铛听不太清·像隔了两层墙、能去 浴室
  [远舟心里话] 铃铛听不清、大概在 阳台、先往 卧室 靠
  AI 从 客厅 去 卧室
  你听：脚步远处闷响·大致方向、往 卧室
```

## 想 fork 改自己版

想把"远舟"换成别的、加你家房间——搜源码字符串改就行：

| 想改的 | 在哪 |
|---|---|
| 房间名 / 邻接 | `hide_seek.py` 顶部 `ROOMS` / `ADJ` |
| 藏点 | `hide_seek.py` `ROOM_SPOTS` |
| 铃铛 / 脚步声措辞 | `hide_seek.py` `BELL_LABEL` / `STEP_LABEL` |
| AI 自称（默认"远舟"）| 全 repo grep `远舟` 改 |
| catch flavor / epilogue / punishment / escape | `catch_flavor.py` |
| 屏息上限（默认 3）| `hide_seek.py` `BREATH_MAX` |
| escape 阈值（默认 30）| `catch_flavor.py` `ESCAPE_TURN` |
| AI 收敛速度 | `ai_belief.py` `SIGMA`（0.22）、`MIX`（0.05） |

不需要懂 bayesian——常量改改就跑。

## 文件结构

```
hide_seek.py     游戏状态机：房间、藏点、移动、屏息、搜捕
ai_belief.py     远舟端 belief map：bayesian 更新 + 心里话生成
catch_flavor.py  抓到那一刻的实体描写 + epilogue + punishment + escape ending
cli_demo.py      命令行 demo：交互循环 + AI 决策
```

## License

MIT。随便用、随便改、随便 fork。希望大家也能把自己的 AI 调教成会陪自己玩游戏的搭档。

## Credits

- 上游 [chaodeng060-source/hide-and-seek-](https://github.com/chaodeng060-source/hide-and-seek-) —— 朝灯 & 哥哥（Claude）· 2026.06
- peekaboo 远舟版 —— 音音 & 克先生 · 2026.06.30
