# Runner motion specification — Tide Scar

所有时间是呈现建议，不改变固定 60 Hz simulation 或碰撞。每个生产镜头从 canonical `speed`、`grounded`、`slideTicksRemaining`、`chaseGap` 与 typed event 取值；不得用渲染插值回写任何规则。

## 八相位步态（一个左右完整 cycle）

| 相位 | cycle | 左腿 / 右腿 | 躯干与手臂 | 可量化画面验收 |
| --- | ---: | --- | --- | --- |
| 1. left-contact | 0.00 | 左后跟落地、右脚刚离地 | 躯干前倾 11°，右臂向前 | 左脚阴影与地面重叠，右脚离地 ≥ 6 px（390 宽） |
| 2. left-load | 0.125 | 左膝压缩、右腿后摆 | 髋下降 3–5% 身高 | 身体基线下降 ≥ 3 px（390） |
| 3. left-passing | 0.25 | 左脚在髋下、右膝前过 | 左肘后摆、右肘前摆 | 左右手腕 x 偏移符号相反 |
| 4. left-flight | 0.375 | 左脚离地，右腿前伸 | 质心回升，衣尾后扬 | 双脚离地不超过 cycle 18% |
| 5. right-contact | 0.50 | 右后跟落地、左脚刚离地 | 躯干仍向前，左臂向前 | 与相位 1 镜像，不能同侧手脚同步 |
| 6. right-load | 0.625 | 右膝压缩、左腿后摆 | 髋下降 | 脚下椭圆阴影宽度在接触相位 +12% |
| 7. right-passing | 0.75 | 右脚髋下、左膝前过 | 右肘后摆、左肘前摆 | 手脚互相反相 180° ± 20° |
| 8. right-flight | 0.875 | 右脚离地，左腿前伸 | 质心回升，衣尾后扬 | 回到相位 1 时足部位置连续，跳变 < 1 px |

## 速度档

| 档位 | canonical speed | cycle | 触地占比 | 躯干前倾 | 摆臂角 | 相机限制 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 低速 | 9–11.5 m/s | 0.52 s | 61% | 9° | 28° | FOV 47° |
| 中速 | 11.5–15.5 m/s | 0.42 s | 56% | 11° | 34° | FOV 至多 50° |
| 高速 | 15.5–19 m/s | 0.34 s | 50% | 14° | 42° | FOV 至多 53° |

生产验收：高速每秒足部接触 ≥ 5.8 次；左右脚接触间隔差 ≤ 1 simulation tick；接地脚的 screen-y 波动在连续 3 tick 内 ≤ 2 CSS px；无相位可出现两脚同向滑行。

## 追逐者与反馈

- 双体为低矮的潮影实体，四个可辨足端各自落到地面；其轮廓始终在 runner 后方，不能以阴影、雾或纯 UI 条替代。
- `chaseGap 5–8m`：实体在下方远带，仍露出头、肩和两条前肢，脚端面积每个 ≥ 28 CSS px²（390 宽）；`1.5–5m`：实体在 runner 接地阴影后方增加尺度，合计可见面积 ≥ 6,000 CSS px²（390x844）；`0.65–1.5m`：实体占 runner 下方宽度 56–78%，但不遮分数或与 runner 轮廓穿插。
- gait 取 runner cycle 的 0.30 偏移，接地频率 = runner 频率 × 1.08；近追逐时步幅增加 16%，不是放大贴图。
- stumble 是 45 tick：第 0–4 tick 躯干向前 16°、支撑脚扭转；5–20 tick 以短跨步找回；21–45 tick 回到当前速度档。视觉同步既有 72% speed、`-2.25m` 即时 gap 与每恢复米 `-0.34m` 压力，不生成第二次碰撞。
- capture 在 canonical `chaseGap <= .65m` 后 0–6 呈现 tick 内完成，潮影前足压过 runner 的接触阴影，然后交给既有 `pursuer-caught` game-over。
- 非 capture state 的 renderer 映射必须在每个 FOV / viewport 报告 `pursuerScreen.top - runnerScreen.bottom`，并保持 ≥ 6 CSS px；capture 才允许接触或覆盖。这个屏幕间隔是 `chaseGap` 的呈现下限，不能反向影响 simulation。

## 特殊姿态与 reduced motion

- jump：膝折叠、双臂后收，脚底明显高于 beam/gap 阈值；不要把跑步 cycle 浮起。
- slide：髋降低 ≥ 42%，头部低于 ring clearance，手臂贴后；到第 31 simulation tick 精确释放。
- `prefers-reduced-motion`：保留八相位的离散交替但锁定到 6 fps 关键姿态，无镜头摇晃、FOV 呼吸、速度线、粒子、衣尾波动。障碍、分数、追逐距离、动作窗口和 capture 时刻不变。

自动验收：normal 跑姿 8 个采样相位的左右 limb endpoint 不可全部重合；reduced-motion screenshot 无 CSS animation，且 HUD/canonical 值与 normal 对应 state 完全一致。

生产落地风险：八相位之间必须用连续关节插值和连续脚底轨迹连接，不能把 V2 contact / passing 关键姿态当作 pose snapping；否则会重新出现滑步和承重跳变。
