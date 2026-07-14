# State and layout specification

## 统一数据源

生产 HUD 只能从 canonical state 取得 `score`、`floor(distance)`、`shards`、`multiplier`、`status`、`chaseGap` 与 milestone event。独立原型将这些字段放入单个 `mockState`；每个按钮只替换整组 state，因此 score / distance / flow / shards 不会互相矛盾。

| 原型 state | score | distance | shards | flow | chaseGap | obstacle |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| normal-run | 1280 | 186 m | 7 | ×1 | 5.7 m | beam |
| close-chase | 1484 | 242 m | 8 | ×1 | 1.35 m | ring |
| milestone | 5101 | 250 m | 1 | ×2 | 4.2 m | column |
| paused | 1484 | 242 m | 8 | ×1 | 1.35 m | gap |

## 精确布局（CSS px）

坐标原点为实际游戏 viewport 左上；所有 HUD 元素在 world canvas 上但在 safe area 内。world 仍是唯一游戏画面，不生成 DOM gameplay entities。

| State | 1440x900 | 390x844 | 844x390 |
| --- | --- | --- | --- |
| ready | score `(30,24)`，distance `(650,24)`，pause `(1374,20,44,44)`；世界从 y=0 | score `(18,106)`，distance `(196,106)`，pause `(328,18,44,44)`；只留一行手势提示 `(18,746)` | score `(14,12)`，distance `(358,12)`，pause `(786,12,44,44)`；不显示提示 |
| normal-run | 同 ready；flow/shards 右对齐于 `(1266,28)` | score `(18,20)`，distance `(196,20)`，flow/shards `(286,106)` | score `(14,12)`，distance `(358,12)`，flow/shards `(645,12)` |
| close-chase | HUD 不位移；潮痕末端在右上 18–58 px 收紧，实体仅占下 28% | HUD 不动；实体最多到 y=748，不盖 score/distance | pursuer 限在 y=276–390，保留 48px 顶部 HUD |
| 250m milestone | `250 m` 沿右路缘，从 horizon 到 y=198 600–900ms | `250 m` 沿路缘 y=318–346，不进入 HUD | `250 m` 沿路缘 y=116–138 |
| stumble | HUD 值不虚构变更；runner pitch 在世界发生，pursuer 前进 | runner 不得低于 y=714，pursuer 不得进入 HUD | runner/pursuer 保持在下半世界 |
| paused | 仅 `canvas` 覆一层 18% 深潮蓝；44 px pause target 融入 HUD 的细竖排并变 resume icon，无孤立方框或全页灰层 | 同左，touch controls 失效但可见 | 同左，无溢出 |
| game-over | world 保留 48% 可见度；结果位于路线中心，不创建全页 modal | 最低留 score/distance 读法；restart 44 px | 结果压缩到世界中心但不碰顶部 HUD |

## 文本与溢出

- HUD 数字使用 `tabular-nums`；score 不截断，最大字号可按 `clamp(28px,5.2vw,54px)` 缩小；distance 保留 `m` 且不能换行。
- 390 宽的主要数值最小 30 px，标签最小 11 px；Pause 和每个原型切换按钮 ≥ 44x44 CSS px。
- `html, body`、shell、canvas 均设置 `overflow:hidden`；自动检查 `scrollWidth === innerWidth`。任何 viewport 下 HUD DOMRect 都须在视口内。
- reduced motion 时布局一像素不变；只有动态潮痕、runner cycle、速度尘和 camera breathing 停止。
