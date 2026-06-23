import type { BlockedReason, Dir, Level, MoveToken, V7Mechanic } from '../engine/types.js';
import { CHAPTER_OF } from '../engine/levels.js';
import { Game, DiptychGame } from './game.js';
import { BoardRenderer } from './render.js';
import {
  loadProgress,
  recordClear,
  setLastPlayed,
  submitScore,
  chapterStats,
  type Progress,
} from './progress.js';

function h<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  props: Partial<HTMLElementTagNameMap[K]> & { class?: string } = {},
  ...children: (Node | string)[]
): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  const { class: cls, ...rest } = props as Record<string, unknown> & { class?: string };
  if (cls) el.className = cls;
  Object.assign(el, rest);
  for (const child of children) el.append(typeof child === 'string' ? document.createTextNode(child) : child);
  return el;
}

const KEY_DIR: Record<string, Dir> = {
  ArrowUp: 'up',
  ArrowDown: 'down',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  w: 'up',
  s: 'down',
  a: 'left',
  d: 'right',
  W: 'up',
  S: 'down',
  A: 'left',
  D: 'right',
};

const MECHANIC_LABEL: Record<V7Mechanic, string> = {
  'core-push': '能量核心',
  'quantum-portal': '量子链接',
  'sync-actors': '同步体',
  'time-shadow': '时间残影',
  'chain-state': '连锁状态',
  'spatial-swap': '空间置换',
  'recursive-room': '递归舱',
  'worldline-split': '世界线分裂',
  'rule-block': '实验参数',
  'misdirection': '误导协议',
  'pull-field': '牵引场',
  'gravity-field': '重力场',
  'mirror-field': '镜像场',
  'ice-vector': '冰轨向量',
  'gate-circuit': '门闩电路',
};

const BLOCKED_TEXT: Record<BlockedReason, string> = {
  wall: '被 containment wall 阻断',
  height: '高度不匹配',
  gate: '量子门闩未开启',
  lock: '权限锁未解除',
  hole: '深坑不可进入',
  crate: '核心无法继续推动',
  shadow: '时间残影占位',
  portal: '链接出口受阻',
  pull: '牵引失败',
  bounds: '越界阻断',
  unknown: '路径受阻',
};

interface CodexEntry {
  key: V7Mechanic;
  icon: string;
  name: string;
  rule: string;
  implication: string;
  anchor: string;
}

const CODEX: CodexEntry[] = [
  {
    key: 'recursive-room',
    icon: 'recursive',
    name: '递归空间',
    rule: '某些能量核心也是可携带的微型实验舱。外部位置和内部状态必须同时被追踪。',
    implication: '先问“这个核心在哪里”，再问“这个核心里面发生了什么”。',
    anchor: 'v7r-017',
  },
  {
    key: 'worldline-split',
    icon: 'branch',
    name: '世界线分裂',
    rule: '两个分支共享输入，但实体状态可以不同。合流要求两个分支同时满足稳定条件。',
    implication: '一个分支提前解决不等于实验结束，真正目标是兼容合流。',
    anchor: 'v7r-019',
  },
  {
    key: 'time-shadow',
    icon: 'echo',
    name: '时间残影',
    rule: '残影延迟复制无人机占位，可以压住量子压板，也会成为阻断体。',
    implication: '把过去的路线当作未来一拍的工具，而不是跟随特效。',
    anchor: 'v7r-011',
  },
  {
    key: 'spatial-swap',
    icon: 'swap',
    name: '空间置换',
    rule: '置换器有明确触发点和交换点。触发后核心或区域按标记交换。',
    implication: '先预判置换后的施力侧，再决定是否触发。',
    anchor: 'v7r-014',
  },
  {
    key: 'sync-actors',
    icon: 'sync',
    name: '同步体',
    rule: '一次输入驱动多个无人机或分支。镜像体会把左右输入反向解释。',
    implication: '阻挡一个分支有时是在给另一个分支校准时机。',
    anchor: 'v7r-008',
  },
  {
    key: 'rule-block',
    icon: 'rule',
    name: '实验参数',
    rule: '规则块是局部插槽，不是全局魔法。本 slice 使用 PUSH/GATE 语义作为轻量入口。',
    implication: '读清楚参数作用域，再判断哪条轨道发生变化。',
    anchor: 'v7r-003',
  },
  {
    key: 'quantum-portal',
    icon: 'portal',
    name: '量子链接',
    rule: '链接只移动无人机，不移动能量核心。它改变施力侧和邻接关系。',
    implication: '入口不是捷径，出口才是新的相邻格。',
    anchor: 'v7r-005',
  },
  {
    key: 'misdirection',
    icon: 'warning',
    name: '误导协议',
    rule: '误导路线必须能从公开规则推理出来，并始终支持撤销。',
    implication: '把最顺手的第一步当作假设来验证，而不是直接相信。',
    anchor: 'v7r-004',
  },
];

function droneSvg(state = 'idle'): string {
  return `<svg class="drone-svg drone-${state}" viewBox="0 0 100 100" aria-hidden="true">
    <defs>
      <radialGradient id="drone-core-${state}" cx="50%" cy="48%" r="48%">
        <stop offset="0%" stop-color="#f3fffd"/>
        <stop offset="54%" stop-color="#59f4df"/>
        <stop offset="100%" stop-color="#0b8a9a"/>
      </radialGradient>
    </defs>
    <ellipse class="drone-shadow" cx="50" cy="88" rx="30" ry="7"/>
    <path class="drone-ring" d="M18 50a32 18 0 1 0 64 0a32 18 0 1 0 -64 0"/>
    <path class="drone-ring vertical" d="M50 18a18 32 0 1 0 0 64a18 32 0 1 0 0 -64"/>
    <circle class="drone-core" cx="50" cy="50" r="21" fill="url(#drone-core-${state})"/>
    <path class="drone-visor" d="M36 48h28l-6 9H42z"/>
    <circle class="drone-thruster left" cx="22" cy="61" r="7"/>
    <circle class="drone-thruster right" cx="78" cy="61" r="7"/>
    <path class="drone-spark" d="M50 6l4 12h-8z"/>
  </svg>`;
}

const NS = 'http://www.w3.org/2000/svg';

export class App {
  private root: HTMLElement;
  private levels: Level[];
  private order: string[];
  private progress: Progress;
  private cleanup: (() => void) | null = null;

  constructor(root: HTMLElement, levels: Level[]) {
    this.root = root;
    this.levels = levels;
    this.order = levels.map((level) => level.id);
    this.progress = loadProgress();
  }

  start(): void {
    this.showMenu();
  }

  private swap(view: HTMLElement): void {
    this.cleanup?.();
    this.cleanup = null;
    view.classList.add('screen-view', 'enter');
    this.root.replaceChildren(view);
    const canUseNativeScroll = !window.navigator.userAgent.toLowerCase().includes('jsdom');
    if (canUseNativeScroll) {
      window.scrollTo(0, 0);
    } else {
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }
    const enter = () => view.classList.add('entered');
    if (window.requestAnimationFrame) window.requestAnimationFrame(enter);
    else window.setTimeout(enter, 0);
  }

  private currentLevel(): Level | undefined {
    return this.levels.find((level) => !this.progress.completed[level.id]) ?? this.levels[0];
  }

  private showMenu(): void {
    const total = this.levels.length;
    const cleared = this.levels.filter((level) => this.progress.completed[level.id]).length;
    const pct = total ? Math.round((cleared / total) * 100) : 0;
    const current = this.currentLevel();
    const stats = chapterStats(this.order, CHAPTER_OF, this.progress);

    const continueBtn = h('button', { class: 'console-command primary' }, '恢复实验');
    continueBtn.onclick = () => current && this.openLevel(current.id);
    const mapBtn = h('button', { class: 'console-command' }, '世界线星图');
    const notesBtn = h('button', { class: 'console-command' }, '研究笔记');
    notesBtn.onclick = () => this.showCodex();
    const recordsBtn = h('button', { class: 'console-command' }, '实验数据');
    recordsBtn.onclick = () => this.showRecords();
    const settingsBtn = h('button', { class: 'console-command' }, '系统校准');
    settingsBtn.onclick = () => this.showSettings();

    const observer = h(
      'section',
      { class: 'home-console' },
      h('div', { class: 'wave-field' }),
      h(
        'div',
        { class: 'observer-shell' },
        h('div', { class: 'observer-core' }, h('div', { class: 'observer-drone' })),
        h('div', { class: 'observer-ring ring-a' }),
        h('div', { class: 'observer-ring ring-b' }),
        h('div', { class: 'observer-ring ring-c' }),
      ),
      h(
        'div',
        { class: 'console-copy' },
        h('span', { class: 'eyebrow' }, 'WORLDLINE LAB / REDESIGN SLICE'),
        h('h1', {}, '量子实验舱'),
        h('p', {}, '读取分支、残影、置换和递归舱状态。当前版本是 20 关 redesign vertical slice，不再沿用旧卡片/棋盘路线。'),
      ),
      h(
        'div',
        { class: 'telemetry-ring' },
        h('b', {}, `${pct}%`),
        h('span', {}, `稳定 ${cleared}/${total}`),
        h('small', {}, current ? `当前实验：${current.name}` : '等待实验载入'),
      ),
      h('nav', { class: 'console-actions' }, continueBtn, mapBtn, notesBtn, recordsBtn, settingsBtn),
    );

    const map = this.worldlineMap(stats, current?.id);
    mapBtn.onclick = () => map.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const menu = h(
      'div',
      { class: 'menu console-menu' },
      observer,
      map,
      this.characterStateSheet(),
    );
    this.swap(menu);
  }

  private worldlineMap(stats: Record<string, { total: number; cleared: number }>, currentId?: string): HTMLElement {
    const section = h(
      'section',
      { class: 'worldline-section', id: 'chapter-map' },
      h(
        'div',
        { class: 'section-heading' },
        h('span', {}, 'WORLDLINE STAR GRAPH'),
        h('h2', {}, '世界线星图'),
        h('p', {}, '节点按实验语法连接，boss 节点使用外环标记；已稳定路径点亮，当前推荐节点脉冲。'),
      ),
    );

    const graph = h('div', { class: 'worldline-graph' });
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'worldline-map');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('preserveAspectRatio', 'none');
    graph.append(svg);

    const chapterOrder = [...new Set(this.levels.map((level) => CHAPTER_OF[level.id] ?? level.chapter ?? '未分组'))];
    const coords = new Map<string, { x: number; y: number }>();
    const nodesByChapter = new Map<string, Level[]>();
    for (const chapter of chapterOrder) nodesByChapter.set(chapter, []);
    for (const level of this.levels) nodesByChapter.get(CHAPTER_OF[level.id] ?? level.chapter ?? '未分组')?.push(level);

    chapterOrder.forEach((chapter, ci) => {
      const levels = nodesByChapter.get(chapter) ?? [];
      const baseX = 11 + ci * (78 / Math.max(1, chapterOrder.length - 1));
      levels.forEach((level, li) => {
        const spread = levels.length === 1 ? 0 : (li - (levels.length - 1) / 2) * 18;
        coords.set(level.id, { x: baseX, y: 50 + spread });
      });
    });

    for (let i = 0; i < this.levels.length - 1; i++) {
      const a = coords.get(this.levels[i]!.id)!;
      const b = coords.get(this.levels[i + 1]!.id)!;
      const line = document.createElementNS(NS, 'line');
      line.setAttribute('class', `worldline-edge${this.progress.completed[this.levels[i]!.id] ? ' lit' : ''}`);
      line.setAttribute('x1', String(a.x));
      line.setAttribute('y1', String(a.y));
      line.setAttribute('x2', String(b.x));
      line.setAttribute('y2', String(b.y));
      svg.append(line);
    }

    chapterOrder.forEach((chapter, ci) => {
      const label = h('div', { class: 'branch-label' }, chapter, h('small', {}, `${stats[chapter]?.cleared ?? 0}/${stats[chapter]?.total ?? 0}`));
      label.style.left = `${11 + ci * (78 / Math.max(1, chapterOrder.length - 1))}%`;
      graph.append(label);
    });

    for (const level of this.levels) {
      const p = coords.get(level.id)!;
      const done = !!this.progress.completed[level.id];
      const boss = level.id.endsWith('004') || level.id.endsWith('007') || level.id.endsWith('010') || level.id.endsWith('013') || level.id.endsWith('016') || level.id.endsWith('018') || level.id.endsWith('020');
      const node = h(
        'button',
        { class: `worldline-node${done ? ' done' : ''}${level.id === currentId ? ' current' : ''}${boss ? ' boss-node' : ''}` },
        h('span', {}, level.id.replace('v7r-', '')),
        h('b', {}, level.name),
      );
      node.style.left = `${p.x}%`;
      node.style.top = `${p.y}%`;
      node.onclick = () => this.openLevel(level.id);
      graph.append(node);
    }

    section.append(graph);
    return section;
  }

  private characterStateSheet(): HTMLElement {
    const states = ['idle', 'move', 'push', 'pull', 'sync', 'teleport', 'split', 'blocked', 'victory'];
    const labels: Record<string, string> = {
      idle: '静止',
      move: '移动',
      push: '推动',
      pull: '牵引',
      sync: '同步',
      teleport: '折跃',
      split: '分裂',
      blocked: '阻断',
      victory: '稳定',
    };
    const rows = states.map((state) =>
      h(
        'div',
        { class: `state-row state-${state}` },
        h('b', {}, labels[state] ?? state),
        ...['s32', 's48', 's64'].map((size) => {
          const cell = h('span', { class: `drone-sample ${size}` });
          cell.innerHTML = droneSvg(state);
          return cell;
        }),
      ),
    );
    return h(
      'section',
      { class: 'character-state-sheet', id: 'character-state-sheet' },
      h('div', { class: 'section-heading' }, h('span', {}, 'QUANTUM DRONE STATES'), h('h2', {}, '量子无人机状态表')),
      h('div', { class: 'state-grid' }, ...rows),
    );
  }

  private openLevel(id: string): void {
    this.playLevel(id);
  }

  private showCodex(): void {
    const list = h('div', { class: 'codex' });
    for (const entry of CODEX) {
      list.append(
        h(
          'div',
          { class: `codex-row codex-${entry.icon}` },
          h('span', { class: 'codex-icon' }),
          h('div', { class: 'codex-body' }, h('b', {}, entry.name), h('span', {}, entry.rule), h('small', {}, entry.implication)),
        ),
      );
    }
    this.overlay(
      h(
        'div',
        { class: 'card help' },
        h('h2', {}, '研究笔记 / 机制档案'),
        h('p', { class: 'result' }, '这里只记录规则、范围和可观察线索，不给完整解法。'),
        list,
      ),
    );
  }

  private showRecords(): void {
    const cleared = this.levels.filter((level) => this.progress.completed[level.id]);
    const rows = cleared.slice(-10).map((level) =>
      h('div', { class: 'record-row' }, h('span', {}, level.name), h('b', {}, `${this.progress.best[level.id] ?? '-'} 步`), h('small', {}, `${this.progress.bestPush[level.id] ?? '-'} 推`)),
    );
    this.overlay(
      h(
        'div',
        { class: 'card help' },
        h('h2', {}, '实验数据'),
        h('p', { class: 'result' }, '记录稳定次数、最少步数、推动数和 replay 证据。'),
        h('div', { class: 'records' }, ...(rows.length ? rows : [h('p', { class: 'result' }, '暂无通关记录。')])),
      ),
    );
  }

  private showSettings(): void {
    this.overlay(
      h(
        'div',
        { class: 'card help' },
        h('h2', {}, '系统校准'),
        h('div', { class: 'settings-list' },
          h('label', {}, h('input', { type: 'checkbox', disabled: true }), ' 高对比度模式'),
          h('label', {}, h('input', { type: 'checkbox', disabled: true }), ' 减少动态效果'),
          h('label', {}, h('input', { type: 'checkbox', disabled: true }), ' 放大世界线节点'),
        ),
        h('p', { class: 'result' }, '这些校准项将在完整 v7 扩展时接入；当前 slice 先保证布局和 replay 稳定。'),
      ),
    );
  }

  private overlay(card: HTMLElement): void {
    const close = h('button', { class: 'primary' }, '返回主控台');
    close.onclick = () => overlay.remove();
    card.append(h('div', { class: 'actions' }, close));
    const overlay = h('div', { class: 'overlay' }, card);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) overlay.remove();
    });
    this.root.append(overlay);
  }

  private mechanicBar(level: Level): HTMLElement {
    const mechanics = level.levelDesignNote?.mechanics ?? level.mechanics ?? [];
    return h('div', { class: 'mechanic-bar' }, ...mechanics.map((m) => h('span', { class: `mechanic-chip m-${m}` }, MECHANIC_LABEL[m])));
  }

  private instruments(level: Level): HTMLElement {
    const items: HTMLElement[] = [];
    const mechanics = new Set(level.mechanics ?? []);
    if (level.recursiveRoom) {
      items.push(h('span', { class: 'instrument recursive-path' }, `层级：Lab > ${level.recursiveRoom.id}`));
    }
    if (level.timeShadow) {
      items.push(h('span', { class: 'instrument echo-queue' }, `残影延迟：${level.timeShadow.delay} 拍`));
    }
    if (level.spatialSwap) {
      items.push(h('span', { class: 'instrument swap-preview' }, level.spatialSwap.trigger === 'replay-only' ? '置换预览：场景标记' : '置换预览：触发后交换'));
    }
    if (level.twin || mechanics.has('worldline-split')) {
      items.push(h('span', { class: 'instrument branch-state' }, level.mirrorTwin ? '分支：A / 镜像 B' : '分支：A / B 合流'));
    }
    if (mechanics.has('rule-block')) {
      items.push(h('span', { class: 'instrument rule-socket' }, '参数槽：PUSH / GATE'));
    }
    if (!items.length) items.push(h('span', { class: 'instrument' }, '观测：标准稳定实验'));
    return h('div', { class: 'instrument-rack' }, ...items);
  }

  private setBlocked(el: HTMLElement, reason: BlockedReason | null): void {
    el.textContent = reason ? BLOCKED_TEXT[reason] : '';
    el.classList.remove('flash');
    if (reason) {
      void el.offsetWidth;
      el.classList.add('flash');
    }
  }

  private playLevel(id: string, resumeLog?: MoveToken[]): void {
    const level = this.levels.find((l) => l.id === id);
    if (!level) return;
    if (level.twin) {
      this.playDiptych(level, resumeLog);
      return;
    }

    const game = new Game(level);
    if (resumeLog?.length) game.loadTokens(resumeLog);
    const saveVisit = () => setLastPlayed(this.progress, { id, at: Date.now(), log: [...game.log], won: game.solved });
    saveVisit();

    const movesEl = h('b', {}, '0');
    const pushesEl = h('b', {}, '0');
    const blockedEl = h('span', { class: 'blocked-feedback', 'aria-live': 'polite' } as Partial<HTMLSpanElement>);
    const hud = h('div', { class: 'hud chamber-hud' },
      h('span', { class: 'stat' }, '步数 ', movesEl),
      h('span', { class: 'stat' }, '推动 ', pushesEl),
      h('span', { class: 'stat' }, `参考 ${level.par ?? '-'}`),
      blockedEl,
    );

    const back = h('button', { class: 'ghost' }, '返回星图');
    back.onclick = () => { saveVisit(); this.showMenu(); };
    const help = h('button', { class: 'ghost' }, '研究笔记');
    help.onclick = () => this.showCodex();
    const topbar = h('div', { class: 'topbar chamber-top' },
      h('div', { class: 'title' }, h('span', {}, level.chapter ?? ''), h('h1', {}, level.name), h('small', {}, level.subtitle)),
      h('div', { class: 'top-actions' }, help, back),
    );

    const boardWrap = h('div', { class: 'board-wrap experiment-table' });
    const renderer = new BoardRenderer(boardWrap);
    renderer.mount(level);
    renderer.update(game.state);

    const undoBtn = h('button', {}, '撤销');
    const restartBtn = h('button', {}, '重开');
    const controls = h('div', { class: 'controls' }, undoBtn, restartBtn, h('span', { class: 'hint-keys' }, '方向键 / WASD 移动，Z 撤销，R 重开'));
    const dpad = this.dpad();

    const screen = h('div', { class: 'game chamber-screen' }, topbar, hud, this.mechanicBar(level), this.instruments(level));
    if (level.intro && !this.progress.completed[id]) screen.append(this.observationLog(level));
    screen.append(h('div', { class: 'experiment-panel' }, boardWrap), controls, dpad);
    this.swap(screen);

    const refresh = () => {
      (undoBtn as HTMLButtonElement).disabled = !game.canUndo;
      movesEl.textContent = String(game.moves);
      pushesEl.textContent = String(game.pushes);
    };
    refresh();

    let locked = false;
    const doMove = (dir: Dir, pull = false) => {
      if (locked) return;
      const res = game.move(dir, pull);
      if (!res) {
        this.setBlocked(blockedEl, game.lastBlockedReason);
        return;
      }
      this.setBlocked(blockedEl, null);
      renderer.update(game.state, res.effect);
      refresh();
      saveVisit();
      if (game.solved) {
        locked = true;
        window.setTimeout(() => this.win(level, game), 320);
      }
    };

    const onKey = (event: KeyboardEvent) => {
      if (event.key in KEY_DIR) {
        event.preventDefault();
        doMove(KEY_DIR[event.key]!, event.shiftKey);
      } else if (event.key === 'z' || event.key === 'Z') {
        if (game.undo()) {
          this.setBlocked(blockedEl, null);
          renderer.update(game.state);
          refresh();
        }
      } else if (event.key === 'r' || event.key === 'R') {
        game.restart();
        this.setBlocked(blockedEl, null);
        renderer.update(game.state);
        refresh();
      } else if (event.key === 'Escape') {
        saveVisit();
        this.showMenu();
      }
    };
    window.addEventListener('keydown', onKey);

    undoBtn.onclick = () => {
      if (game.undo()) {
        this.setBlocked(blockedEl, null);
        renderer.update(game.state);
        refresh();
      }
    };
    restartBtn.onclick = () => {
      game.restart();
      this.setBlocked(blockedEl, null);
      renderer.update(game.state);
      refresh();
    };
    this.bindDpad(dpad, doMove);
    window.addEventListener('resize', () => renderer.sizeToViewport());
    this.cleanup = () => window.removeEventListener('keydown', onKey);
  }

  private playDiptych(level: Level, resumeLog?: MoveToken[]): void {
    const game = new DiptychGame(level);
    if (resumeLog?.length) game.loadTokens(resumeLog);
    const saveVisit = () => setLastPlayed(this.progress, { id: level.id, at: Date.now(), log: [...game.log], won: game.solved });
    saveVisit();

    const movesEl = h('b', {}, '0');
    const pushesEl = h('b', {}, '0');
    const blockedEl = h('span', { class: 'blocked-feedback', 'aria-live': 'polite' } as Partial<HTMLSpanElement>);
    const hud = h('div', { class: 'hud chamber-hud' },
      h('span', { class: 'stat' }, '步数 ', movesEl),
      h('span', { class: 'stat' }, '推动 ', pushesEl),
      h('span', { class: 'stat' }, `参考 ${level.par ?? '-'}`),
      blockedEl,
    );

    const back = h('button', { class: 'ghost' }, '返回星图');
    back.onclick = () => { saveVisit(); this.showMenu(); };
    const topbar = h('div', { class: 'topbar chamber-top' },
      h('div', { class: 'title' }, h('span', {}, level.chapter ?? ''), h('h1', {}, level.name), h('small', {}, level.subtitle)),
      h('div', { class: 'top-actions' }, h('button', { class: 'ghost', onclick: () => this.showCodex() } as Partial<HTMLButtonElement>, '研究笔记'), back),
    );

    const wrapA = h('div', { class: 'board-wrap experiment-table branch-a' });
    const wrapB = h('div', { class: 'board-wrap experiment-table branch-b' });
    const rendererA = new BoardRenderer(wrapA);
    const rendererB = new BoardRenderer(wrapB);
    rendererA.mount(level);
    rendererB.mount(level.twin!);
    rendererA.update(game.a);
    rendererB.update(game.b);

    const pair = h('div', { class: 'diptych branch-lanes' },
      h('div', { class: 'branch-panel' }, h('b', {}, 'Branch A'), wrapA),
      h('div', { class: 'branch-panel' }, h('b', {}, level.mirrorTwin ? 'Mirror B' : 'Branch B'), wrapB),
    );
    const undoBtn = h('button', {}, '撤销');
    const restartBtn = h('button', {}, '重开');
    const controls = h('div', { class: 'controls' }, undoBtn, restartBtn, h('span', { class: 'hint-keys' }, '一次输入驱动两条世界线；Z 撤销，R 重开'));
    const dpad = this.dpad();

    const screen = h('div', { class: 'game chamber-screen' }, topbar, hud, this.mechanicBar(level), this.instruments(level));
    if (level.intro && !this.progress.completed[level.id]) screen.append(this.observationLog(level));
    screen.append(h('div', { class: 'experiment-panel' }, pair), controls, dpad);
    this.swap(screen);

    const refresh = () => {
      (undoBtn as HTMLButtonElement).disabled = !game.canUndo;
      movesEl.textContent = String(game.moves);
      pushesEl.textContent = String(game.pushes);
    };
    refresh();

    let locked = false;
    const doMove = (dir: Dir, pull = false) => {
      if (locked) return;
      const res = game.move(dir, pull);
      if (!res) {
        this.setBlocked(blockedEl, game.lastBlockedReason);
        return;
      }
      this.setBlocked(blockedEl, null);
      rendererA.update(game.a, res.a.effect);
      rendererB.update(game.b, res.b.effect);
      refresh();
      saveVisit();
      if (game.solved) {
        locked = true;
        window.setTimeout(() => this.win(level, game), 340);
      }
    };

    const onKey = (event: KeyboardEvent) => {
      if (event.key in KEY_DIR) {
        event.preventDefault();
        doMove(KEY_DIR[event.key]!, event.shiftKey);
      } else if (event.key === 'z' || event.key === 'Z') {
        if (game.undo()) {
          rendererA.update(game.a);
          rendererB.update(game.b);
          refresh();
        }
      } else if (event.key === 'r' || event.key === 'R') {
        game.restart();
        rendererA.update(game.a);
        rendererB.update(game.b);
        refresh();
      } else if (event.key === 'Escape') {
        saveVisit();
        this.showMenu();
      }
    };
    window.addEventListener('keydown', onKey);
    undoBtn.onclick = () => {
      if (game.undo()) {
        rendererA.update(game.a);
        rendererB.update(game.b);
        refresh();
      }
    };
    restartBtn.onclick = () => {
      game.restart();
      rendererA.update(game.a);
      rendererB.update(game.b);
      refresh();
    };
    this.bindDpad(dpad, doMove);
    this.cleanup = () => window.removeEventListener('keydown', onKey);
  }

  private observationLog(level: Level): HTMLElement {
    return h('div', { class: 'observation-log' }, h('b', {}, '观测注记'), h('span', {}, level.intro));
  }

  private dpad(): HTMLElement {
    return h('div', { class: 'dpad' },
      h('button', { class: 'up' }, '↑'),
      h('button', { class: 'left' }, '←'),
      h('button', { class: 'right' }, '→'),
      h('button', { class: 'down' }, '↓'),
    );
  }

  private bindDpad(dpad: HTMLElement, handler: (dir: Dir) => void): void {
    (dpad.querySelector('.up') as HTMLButtonElement).onclick = () => handler('up');
    (dpad.querySelector('.down') as HTMLButtonElement).onclick = () => handler('down');
    (dpad.querySelector('.left') as HTMLButtonElement).onclick = () => handler('left');
    (dpad.querySelector('.right') as HTMLButtonElement).onclick = () => handler('right');
  }

  private win(level: Level, game: Game | DiptychGame): void {
    setLastPlayed(this.progress, { id: level.id, at: Date.now(), log: [...game.log], won: true });
    const outcome = recordClear(this.progress, level.id, {
      moves: game.moves,
      pushes: game.pushes,
      par: level.par ?? Infinity,
      usedUndo: game.usedUndo,
    });
    void submitScore(level.id, game.moves, game.pushes, game.log);

    const index = this.order.indexOf(level.id);
    const nextId = index >= 0 ? this.order[index + 1] : undefined;
    const nextButton = nextId
      ? h('button', { class: 'primary' }, '下一实验')
      : h('button', { class: 'primary' }, '返回主控台');
    nextButton.onclick = () => {
      overlay.remove();
      if (nextId) this.playLevel(nextId);
      else this.showMenu();
    };
    const mapButton = h('button', {}, '世界线星图');
    mapButton.onclick = () => {
      overlay.remove();
      this.showMenu();
    };

    const card = h('div', { class: 'card win-collapse' },
      h('div', { class: 'collapse-core' }),
      h('h2', {}, '实验稳定'),
      h('p', { class: 'result' }, `世界线收束于 ${game.moves} 步 / ${game.pushes} 推。${outcome.parHit ? '达到参考稳定线。' : '已记录 replay，可继续优化。'}`),
      h('div', { class: 'win-medals' },
        h('span', { class: `chip${outcome.parHit ? ' on' : ''}` }, outcome.parHit ? 'PAR 稳定' : 'PAR 待优化'),
        h('span', { class: `chip${outcome.clean ? ' on' : ''}` }, outcome.clean ? '无撤销' : '使用过撤销'),
      ),
      h('div', { class: 'actions' }, mapButton, nextButton),
    );
    const overlay = h('div', { class: 'overlay' }, card);
    this.root.append(overlay);
  }
}
