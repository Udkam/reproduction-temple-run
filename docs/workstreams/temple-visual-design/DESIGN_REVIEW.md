# Design review — Tide Scar V2 candidate

## What changes in the visual language

| 当前 TR2 观察到的缺口 | Tide Scar 决定 | 可复核结果 |
| --- | --- | --- |
| 泛化的低多边形/雾景容易显出 AI 拼贴感 | 沙面、深潮影、珊瑚只在切口出现；远崖/信标、中景潮池石块、近路缘碎屑建立三层深度 | 没有玻璃、霓虹、网格、标签或卡阵；道路以矿物边缘而非丛林物件成立 |
| runner 是可见的分件，但 contact/passing 不够一眼可读 | 八相位、左右反相、前倾、接地压缩和速度档 | 原型绘制左/右足、膝、肘分离；`stride-contact-pass.png` 比较 0.00/0.25 phase |
| 追逐者接近时只是底部堆叠，压力不可量化 | 低潮双体有头、肩、四肢和接地影，随 canonical `chaseGap` 改变 y、尺度、步频 | close-chase 的 pursuer clipped area 为正，且非 capture 与 runner 保持 ≥ 6 px；潮痕线仅作辅助，不替代实体 |
| 速度增长没有强的身体反馈 | 9–19m/s 映射 0.52→0.34s cycle、61→50% contact、9→14° lean | `RUNNER_MOTION_SPEC.md` 逐档给出可测频率与角度；不改变 simulation timing |
| beam/ring/column/gap 在远处形状层次会互相混淆 | 横梁/门孔/偏心柱/断路双唇各有负空间和形状规则 | 每类 prototype 截图有独立 positive clipped bounds；颜色不是唯一线索 |
| score、米数和资源容易被分散的 HUD 语言稀释 | score 第一、distance 第二，flow/shards 降级；一个 mock state 同时驱动所有数值 | 自动检查读 HTML HUD 并与 `mockState` 完全比较；数字不截断、distance 始终带 m |
| portrait 的品牌/提示挤占路线 | 先固定 390x844：HUD 顶部 20px，pause 融入竖排；正式 capture 隐藏原型控制器 | DOMRect gate 覆盖 desktop/portrait/landscape；无水平溢出 |
| 横屏为了压缩 HUD 而丢失资源指标 | 844x390 改为 44 px 四列/双行 typographic rail：score、distance 占左两列，完整 `flow ×n` / `shards n` 占右两行，pause 保留 44px target | 自动检查四项均可见、文本来自同一 mockState、在 viewport 内，彼此及 runner/pursuer/obstacle clipped bounds 的 intersection area 均为 0 |
| 250m 中央提示会与 column 的轮廓竞争 | `250 m` 只作为右路缘 / 潮痕附近的短暂世界标记；不改变追逐、障碍或 HUD 的 canonical 值 | 390x844 marker 的 road-edge distance 为 56.38 CSS px（gate: 18–96），与 HUD、runner、pursuer、column 的每项 intersection area 都是 0 |

## 自动 acceptance

运行 `python verify_tide_scar.py --base-url http://127.0.0.1:4173` 后，`prototype-acceptance.json` 必须同时证明：

1. 1440x900、390x844、844x390 每个 capture 都是单一 canvas，`overflowX=0`；HUD 和 pause 的 DOMRect 完全在 viewport 内。
2. score、distance、flow、shards 与从 JS 读取的同一个 `mockState` 相等；数值非占位文本。
3. 文字/背景 `hudOnSky` ≥ 4.5:1；潮痕/潮影、珊瑚/沙面分别记录对比度。珊瑚不是唯一危险编码，bounds kind 仍是明确 `beam/ring/column/gap`。
4. runner、pursuer、每个 obstacle 均报告 viewport-clipped CSS bounds；normal/close chase 的 pursuer area > 0，四类 obstacle area > 0。
5. normal、chase、milestone、paused 和四类障碍均产生 PNG 与 SHA-256；没有 console error；`prefers-reduced-motion` 仍保留相同 HUD/state 且在诊断中为 true。
6. 每个 non-capture capture 报告正的 `pursuerGapPx`，最低为 6 CSS px；V2 的 390 portrait normal/close 预览分别是 110.93 / 55.29 px，1440 desktop preview 是 72.45 px。
7. 本次 P1 定向命令仅重捕 `mobile-landscape` 与 `mobile-milestone`：前者证明四项完整 metric 都可见、无互撞/世界关键轮廓碰撞；后者证明 marker 处于 18–96 CSS px right-road-edge 区间且八项目标 intersection area 皆为 0。未受影响的九张 PNG 保留其原 SHA-256 记录。

这些是原型的可视化 gate，不宣称替代生产项目的 canonical replay、Three.js renderer、真实 touch 或 QA evidence。

## 生产移植约束

- 仅在未来获授权时，把 tokens / motion mapping 迁入 Three.js；不要把 Canvas 原型、mock values 或 DOM 作为生产实体。
- 继续使用当前 renderer 已报告的 pursuer / obstacle clipped bounds；把本规范的 shape gate 接到同一 evidence 报告。
- 一切 score、distance、shards、flow、milestone、stumble、capture 的开始/结束由 canonical state 或 typed event 决定。表现系统只读取。

## 剩余风险

- 指定视频无法在本环境观看，视频关键帧没有作为决策证据；公开官方页面只贡献高层玩法原则。
- 八相位在生产 renderer 中必须连续插值，不能将 contact / passing pose 逐帧 snapping；真实三维关节遮挡、camera yaw 和低端机 GPU 仍需获授权后的独立验证。
- canonical `chaseGap` 到屏幕间隔的映射必须随 FOV / viewport 重算，且在非 capture 时保留 ≥ 6 CSS px；本原型的屏幕间隔不可以反写规则。
- 当前生产候选已被接受；本文是 design-only candidate，不构成向稳定分支写入、合并或修改规则的授权。
