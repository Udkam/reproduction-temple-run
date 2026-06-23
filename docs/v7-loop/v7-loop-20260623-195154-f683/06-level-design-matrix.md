# Level Design Matrix

RUN_ID: `v7-loop-20260623-195154-f683`

Status: Stage 10 redesign runtime exposes a 20/20 vertical slice. The previous 70-level checkpoint is product-rejected and no longer the accepted runtime target.

## Current 20-Level Redesign Slice

| ID | Title | Group | Mechanics | Core question | Solver status | Par |
| --- | --- | --- | --- | --- | --- | ---: |
| v7r-001 | 第一稳定器 | 启动序列 | core-push | What does a core stabilize? | verified-replay | 3 |
| v7r-002 | 阻断读数 | 启动序列 | core-push, misdirection | Why did the push fail? | verified-replay | 4 |
| v7r-003 | 参数插槽 | 启动序列 | rule-block, gate-circuit | What changes when PUSH is socketed? | verified-replay | 4 |
| v7r-004 | 短路陷阱 | 启动序列 | core-push, misdirection | Why is the short route wrong? | verified-replay | 8 |
| v7r-005 | 成对折跃 | 量子链接 | quantum-portal | How does a link change adjacency? | verified-replay | 4 |
| v7r-006 | 旋向出口 | 量子链接 | quantum-portal | What does exit orientation imply? | verified-replay | 4 |
| v7r-007 | 过滤链接 | 量子链接 | quantum-portal, rule-block | Which objects may pass? | verified-replay | 7 |
| v7r-008 | 双体制动 | 同步体 | sync-actors | How can one input solve two branches? | verified-replay | 3 |
| v7r-009 | 镜像夹持 | 同步体 | sync-actors, mirror-field | How does symmetry become useful? | verified-replay | 3 |
| v7r-010 | 分轨插槽 | 同步体 | sync-actors, rule-block | Can a local rule affect each lane? | verified-replay | 4 |
| v7r-011 | 残影门闩 | 时间残影 | time-shadow, gate-circuit | How can the past hold a gate? | verified-replay | 3 |
| v7r-012 | 未来推力 | 时间残影 | time-shadow, core-push | How do I prepare a future push line? | verified-replay | 4 |
| v7r-013 | 碰撞预报 | 时间残影 | time-shadow, misdirection | Why is backtracking risky? | verified-replay | 5 |
| v7r-014 | 双点交换 | 空间置换 | spatial-swap | What actually moves in a swap? | manual-reviewed | 4 |
| v7r-015 | 移动靶环 | 空间置换 | spatial-swap, core-push | When should the target relation move? | manual-reviewed | 5 |
| v7r-016 | 链接重接 | 空间置换 | spatial-swap, quantum-portal | How do link and swap language interact? | manual-reviewed | 4 |
| v7r-017 | 进入胶囊 | 递归舱 | recursive-room | What is inside a chamber-core? | manual-reviewed | 3 |
| v7r-018 | 移动房间 | 递归舱 | recursive-room, quantum-portal | Why move a room before entering it? | manual-reviewed | 3 |
| v7r-019 | 分支合流 | 误导协议 | worldline-split, sync-actors | Why does one solved branch still fail? | manual-reviewed | 3 |
| v7r-020 | 不稳定协议 | 误导协议 | rule-block, time-shadow, spatial-swap | Which law is the actual constraint? | manual-reviewed | 8 |

## Counts

| Group | Count |
| --- | ---: |
| 第 1 章：启动序列 | 4 |
| 第 2 章：量子链接 | 3 |
| 第 3 章：同步体 | 3 |
| 第 4 章：时间残影 | 3 |
| 第 5 章：空间置换 | 3 |
| 第 6 章：递归舱 | 2 |
| 第 7 章：误导协议 | 2 |

Total: 20/20.

## QA Notes

- `npm run verify` must pass every stored replay.
- `npm run audit:levels` now fails unless exactly 20 redesign slice levels are exposed.
- The slice covers recursive space, worldline split, time echo, spatial swap, multi-drone sync, rule blocks, portals, and misdirection.
- This slice is not the final 70-level expansion. The 70-level target resumes only after redesign visuals and puzzle language pass QA.
