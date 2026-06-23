# Level Design Matrix

This file will contain all 70 final levels before full buildout is accepted.

## Chapter structure

| Chapter | Count | Focus |
|---|---:|---|
| 启动序列 | 8 | movement, push, targets, undo, core UI |
| 量子门 | 8 | portals, direction mapping, crate/energy portal rules |
| 同步体 | 8 | multi-actor sync, mirror, delay, different actor properties |
| 时间残影 | 8 | delayed echoes, history windows, simultaneous pads |
| 空间置换 | 8 | cell/room/object swaps and route reconstruction |
| 递归舱 | 8 | lightweight room-in-block recursion |
| 连锁实验 | 8 | chapter state and fair linked consequences |
| 误导协议 | 8 | fair misdirection and reversible traps |
| 终局收束 | 6 | boss puzzles combining multiple mechanisms |

## Required per-level record

```ts
{
  id: string,
  title: string,
  chapter: string,
  mechanics: string[],
  coreIdea: string,
  trick: string,
  fairness: string,
  difficulty: 1 | 2 | 3 | 4 | 5,
  solverStatus: "optimal" | "verified-replay" | "manual-reviewed",
  par: number | null,
  solution: unknown[]
}
```

Any level missing this record does not count toward the 70-level target.
