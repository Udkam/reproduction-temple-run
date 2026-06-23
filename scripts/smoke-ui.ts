import { JSDOM } from 'jsdom';
import type { Dir } from '../src/engine/types.js';
import { LEVELS } from '../src/engine/levels.js';

const DIR_KEY: Record<Dir, string> = {
  up: 'ArrowUp',
  down: 'ArrowDown',
  left: 'ArrowLeft',
  right: 'ArrowRight',
};

const dom = new JSDOM('<!doctype html><html><body><div id="app"></div></body></html>', {
  url: 'http://localhost/',
  pretendToBeVisual: true,
});
const w = dom.window as unknown as typeof globalThis & Window;
const g = globalThis as Record<string, unknown>;
g.window = w;
g.document = w.document;
g.localStorage = w.localStorage;
g.KeyboardEvent = w.KeyboardEvent;
g.requestAnimationFrame = w.requestAnimationFrame.bind(w);

const { App } = await import('../src/web/ui.js');

const sleep = (ms: number) => new Promise((resolve) => w.setTimeout(resolve, ms));
const root = w.document.getElementById('app')!;
const app = new App(root as unknown as HTMLElement, LEVELS);
app.start();

let failures = 0;
console.log('\nDriftbox redesign UI smoke test (jsdom)');
console.log('-'.repeat(72));

for (const level of LEVELS) {
  const node = [...root.querySelectorAll('.worldline-node')]
    .find((button) => (button.textContent ?? '').includes(level.id.replace('v7r-', ''))) as HTMLElement | undefined;
  if (!node) {
    console.log(`FAIL ${level.id} node not found`);
    failures++;
    continue;
  }
  node.click();
  if (!root.querySelector('.chamber-screen .board-wrap')) {
    console.log(`FAIL ${level.id} chamber did not open`);
    failures++;
    continue;
  }
  for (const token of level.solution ?? []) {
    const pull = token.startsWith('@');
    const dir = (pull ? token.slice(1) : token) as Dir;
    w.dispatchEvent(new w.KeyboardEvent('keydown', { key: DIR_KEY[dir], shiftKey: pull, bubbles: true }));
  }
  await sleep(720);
  const won = !!root.querySelector('.overlay .win-collapse');
  if (!won) {
    console.log(`FAIL ${level.id} ${level.name} win overlay never appeared`);
    failures++;
  } else {
    console.log(`PASS ${level.id} ${level.name} played=${level.solution?.length ?? 0}`);
  }
  const mapBtn = [...root.querySelectorAll('.overlay .actions button')]
    .find((button) => (button.textContent ?? '').includes('世界线星图')) as HTMLElement | undefined;
  mapBtn?.click();
  await sleep(20);
}

console.log('-'.repeat(72));
if (failures > 0) {
  console.error(`${failures} UI smoke check(s) FAILED.`);
  process.exit(1);
}
console.log('All redesign levels playable to a win through the real UI.');
