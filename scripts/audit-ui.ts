import { JSDOM } from 'jsdom';
import { LEVELS } from '../src/engine/levels.js';
import { App } from '../src/web/ui.js';

let failures = 0;
function check(condition: boolean, label: string): void {
  console.log(`${condition ? 'PASS' : 'FAIL'} ${label}`);
  if (!condition) failures++;
}

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

const root = w.document.getElementById('app')!;
const app = new App(root as unknown as HTMLElement, LEVELS);
app.start();

const text = () => root.textContent ?? '';
const buttonByText = (needle: string): HTMLElement | undefined =>
  [...root.querySelectorAll('button')].find((button) => (button.textContent ?? '').includes(needle)) as HTMLElement | undefined;

console.log('\nDriftbox redesign UI audit');
console.log('-'.repeat(72));

check(!!root.querySelector('.home-console'), 'quantum experiment console home exists');
check(!!root.querySelector('.observer-shell') && !!root.querySelector('.observer-core'), 'central observer device exists');
check(!!buttonByText('恢复实验'), 'resume experiment command exists');
check(!!buttonByText('世界线星图'), 'worldline map command exists');
check(!!buttonByText('研究笔记'), 'research notes command exists');
check(!!buttonByText('实验数据'), 'experiment data command exists');
check(!!buttonByText('系统校准'), 'system calibration command exists');
check(!!root.querySelector('.worldline-section'), 'worldline section exists');
check(!!root.querySelector('svg.worldline-map'), 'worldline SVG map exists');
check(root.querySelectorAll('.worldline-edge').length >= LEVELS.length - 1, 'worldline edges connect levels');
check(root.querySelectorAll('.worldline-node').length === 20, '20 worldline level nodes exist');
check(!!root.querySelector('.boss-node'), 'boss node shape exists');
check(!!root.querySelector('.character-state-sheet'), 'character state sheet exists');
check(root.querySelectorAll('.state-row').length >= 9, 'character sheet lists required states');
check(!root.querySelector('.level-grid'), 'card-grid level selector is absent');
check(!text().includes('2.5D') && !text().includes('立体演示'), 'no visible 2.5D/3D entry text');

buttonByText('研究笔记')?.click();
check(!!root.querySelector('.codex'), 'mechanism archive overlay opens');
check(['递归空间', '世界线分裂', '时间残影', '空间置换', '同步体', '实验参数'].every((label) => text().includes(label)), 'archive covers redesign mechanisms');
root.querySelector('.overlay button')?.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

buttonByText('系统校准')?.click();
check(text().includes('高对比度') && text().includes('减少动态'), 'settings/calibration overlay opens');
root.querySelector('.overlay button')?.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

buttonByText('实验数据')?.click();
check(text().includes('实验数据'), 'experiment data overlay opens');
root.querySelector('.overlay button')?.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

const firstNode = root.querySelector('.worldline-node') as HTMLElement | null;
firstNode?.click();
check(!!root.querySelector('.chamber-screen'), 'chamber screen opens');
check(!!root.querySelector('.hud'), 'chamber HUD exists');
check(!!root.querySelector('.mechanic-bar .mechanic-chip'), 'mechanic chips exist');
check(!!root.querySelector('.instrument-rack .instrument'), 'mechanic instruments exist');
check(!!root.querySelector('.experiment-panel .board-wrap'), 'experiment panel wraps board');
check(!!root.querySelector('.player .drone-core'), 'quantum drone avatar renders');
check(!!buttonByText('撤销') && !!buttonByText('重开'), 'undo and restart controls exist');

w.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
check((root.querySelector('.blocked-feedback')?.textContent ?? '').length > 0, 'blocked movement feedback appears');

for (const token of LEVELS[0]!.solution ?? []) {
  const dir = token.startsWith('@') ? token.slice(1) : token;
  const key = dir === 'right' ? 'ArrowRight' : dir === 'left' ? 'ArrowLeft' : dir === 'up' ? 'ArrowUp' : 'ArrowDown';
  w.dispatchEvent(new w.KeyboardEvent('keydown', { key, shiftKey: token.startsWith('@'), bubbles: true }));
}
await new Promise((resolve) => w.setTimeout(resolve, 750));
check(!!root.querySelector('.overlay .win-collapse'), 'victory collapse overlay appears');
check(!!buttonByText('下一实验'), 'next experiment button exists on win overlay');

const css = await import('node:fs').then((fs) => fs.readFileSync('src/web/styles.css', 'utf8'));
check(/@media\s*\(max-width:\s*(900|760|620)px\)/.test(css), 'mobile media query exists');
check(css.includes('overflow-x: hidden'), 'mobile horizontal overflow guard exists');
check(css.includes('.worldline-graph') && css.includes('.home-console') && css.includes('.experiment-panel'), 'redesign CSS landmarks exist');

console.log('-'.repeat(72));
if (failures) {
  console.error(`${failures} UI audit check(s) failed.`);
  process.exit(1);
}
console.log('All UI audit checks passed.');
