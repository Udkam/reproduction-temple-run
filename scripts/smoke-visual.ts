import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { chromium, type Page } from 'playwright';
import { createServer } from 'vite';
import { LEVELS } from '../src/engine/levels.js';
import type { MoveToken } from '../src/engine/types.js';

const RUN_ID = 'v7-loop-20260623-195154-f683';
const OUT_DIR = join('docs', 'v7-loop', RUN_ID, 'screenshots');

const KEY: Record<string, string> = {
  up: 'ArrowUp',
  down: 'ArrowDown',
  left: 'ArrowLeft',
  right: 'ArrowRight',
};

async function playSolution(page: Page, solution: MoveToken[]): Promise<void> {
  for (const token of solution) {
    const pull = token.startsWith('@');
    const dir = pull ? token.slice(1) : token;
    const key = KEY[dir];
    if (!key) throw new Error(`Unknown solution token ${token}`);
    if (pull) await page.keyboard.down('Shift');
    await page.keyboard.press(key);
    if (pull) await page.keyboard.up('Shift');
  }
}

async function openHome(page: Page, baseUrl: string): Promise<void> {
  await page.goto(baseUrl);
  await page.waitForSelector('.home-console');
}

async function openLevel(page: Page, id: string): Promise<void> {
  const index = LEVELS.findIndex((level) => level.id === id);
  if (index < 0) throw new Error(`Unknown level id ${id}`);
  const label = id.replace('v7r-', '');
  const node = page.locator('.worldline-node', { hasText: label }).first();
  await node.scrollIntoViewIfNeeded();
  await node.click();
  await page.waitForSelector('.chamber-screen .board-wrap');
}

async function shot(page: Page, name: string): Promise<void> {
  await page.waitForSelector('.screen-view.entered');
  await page.waitForTimeout(180);
  await page.screenshot({ path: join(OUT_DIR, `${name}.png`), fullPage: true });
}

await mkdir(OUT_DIR, { recursive: true });

const vite = await createServer({
  logLevel: 'silent',
  server: { host: '127.0.0.1', port: 0 },
});
await vite.listen();
const baseUrl = vite.resolvedUrls?.local[0];
if (!baseUrl) throw new Error('Vite did not provide a local URL');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });

try {
  await openHome(page, baseUrl);
  await shot(page, '01-home-console');

  await page.locator('#chapter-map').scrollIntoViewIfNeeded();
  await shot(page, '02-worldline-star-graph');

  const levelShots: Array<[string, string]> = [
    ['03-level-001', 'v7r-001'],
    ['04-portal-005', 'v7r-005'],
    ['05-sync-008', 'v7r-008'],
    ['06-time-echo-011', 'v7r-011'],
    ['07-spatial-swap-014', 'v7r-014'],
    ['08-recursive-017', 'v7r-017'],
    ['09-misdirection-019', 'v7r-019'],
  ];
  for (const [name, id] of levelShots) {
    await openHome(page, baseUrl);
    await openLevel(page, id);
    await shot(page, name);
  }

  await openHome(page, baseUrl);
  await page.locator('#character-state-sheet').scrollIntoViewIfNeeded();
  await shot(page, '10-character-state-sheet');

  await openHome(page, baseUrl);
  await openLevel(page, 'v7r-001');
  await playSolution(page, LEVELS[0]!.solution ?? []);
  await page.waitForSelector('.overlay .win-collapse');
  await shot(page, '11-victory-collapse');

  await page.setViewportSize({ width: 390, height: 844 });
  await openHome(page, baseUrl);
  await shot(page, '12-mobile-home');
  await openLevel(page, 'v7r-011');
  await shot(page, '13-mobile-level');
} finally {
  await browser.close();
  await vite.close();
}

console.log(`Visual smoke screenshots written to ${OUT_DIR}`);
