// Dev-only stepped visual test level for the isometric renderer. NOT part of the
// catalog (LEVELS) — it never affects level counts or progress. Showcases:
// height 0/1/2 staircase, a portal that lifts the player to a high ledge, a
// crate pushed DOWN the staircase to the goal, and a tall wall for occlusion.
import type { Level } from '../engine/types.js';
import { parseLevel } from '../engine/level.js';

let cached: Level | null = null;

export function makeDemoLevel(): Level {
  if (cached) return cached;
  cached = parseLevel({
    id: 'demo',
    name: '立体演示',
    subtitle: 'Iso Demo',
    intro: '等轴演示关：下台阶 / 把箱子推下 / 折跃门连接高低 / 高墙遮挡。走到折跃门会被送上高台。',
    par: 5,
    map: [
      '#########',
      '#@   #  #',
      '# ## # ##',
      '#o . $ o#',
      '# ##### #',
      '#       #',
      '#########',
    ],
    heights: [
      '         ',
      '         ',
      '         ',
      '    1222 ',
      '         ',
      '         ',
      '         ',
    ],
    solution: ['down', 'down', 'left', 'left', 'left'],
  });
  return cached;
}
