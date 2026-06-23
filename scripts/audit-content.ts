import { readFileSync } from 'node:fs';
import { LEVELS } from '../src/engine/levels.js';

const RUN_ID = 'v7-loop-20260623-195154-f683';
const files = {
  readme: readFileSync('README.md', 'utf8'),
  claude: readFileSync('claude.md', 'utf8'),
  report: readFileSync(`docs/v7-loop/${RUN_ID}/10-acceptance-report.md`, 'utf8'),
  art: readFileSync(`docs/v7-loop/${RUN_ID}/07-art-direction.md`, 'utf8'),
  matrix: readFileSync(`docs/v7-loop/${RUN_ID}/06-level-design-matrix.md`, 'utf8'),
  reference: readFileSync(`docs/v7-loop/${RUN_ID}/11-reference-study.md`, 'utf8'),
  redesign: readFileSync(`docs/v7-loop/${RUN_ID}/12-redesign-spec.md`, 'utf8'),
  grammar: readFileSync(`docs/v7-loop/${RUN_ID}/13-puzzle-grammar.md`, 'utf8'),
  uiRedesign: readFileSync(`docs/v7-loop/${RUN_ID}/14-ui-redesign-spec.md`, 'utf8'),
  slice20: readFileSync(`docs/v7-loop/${RUN_ID}/15-vertical-slice-20-report.md`, 'utf8'),
};

let failures = 0;
function check(condition: boolean, label: string): void {
  console.log(`${condition ? 'PASS' : 'FAIL'} ${label}`);
  if (!condition) failures++;
}

console.log('\nDriftbox content audit');
console.log('-'.repeat(72));

check(LEVELS.length === 20, `runtime exposes 20 redesign slice levels (actual ${LEVELS.length})`);
check(files.readme.includes('20-level vertical slice') && files.readme.includes('not the final 70-level target'), 'README references current 20-level slice and non-final 70 status');
check(files.readme.includes('v7-loop-20260623-195154-f683'), 'README links current RUN_ID');
check(files.claude.includes('20-level vertical slice') && files.claude.includes('not the final 70-level product'), 'claude.md references current 20-level slice and non-final 70 status');
check(files.claude.includes('v7-loop-20260623-195154-f683'), 'claude.md links current RUN_ID');
check(files.matrix.includes('20/20') && files.matrix.includes('v7r-020'), 'level matrix records current 20-level redesign slice status');
check(files.art.includes('No external images') && files.art.includes('No external'), 'art direction records external asset/license status');
check(files.report.includes('Stage 10 redesign slice implemented') && files.report.includes('not final 70-level accepted'), 'acceptance report records current Stage 10 status honestly');
check(files.reference.includes("Patrick's Parabox") && files.reference.includes('Baba Is You') && files.reference.includes('茜塔和世界线悖论'), 'reference study covers required games');
check(files.redesign.includes('20-level vertical slice') && /Six Core Systems/i.test(files.redesign), 'redesign spec records 20-level slice and system scope');
check(files.grammar.includes('Recursive Space System') && files.grammar.includes('Rule Block / Experiment Parameter System'), 'puzzle grammar covers recursive space and rule blocks');
check(files.uiRedesign.includes('Quantum Experiment Console') && files.uiRedesign.includes('Worldline Star Graph'), 'UI redesign spec rejects card-grid route');
check(files.slice20.includes('Status: implemented in runtime') && files.slice20.includes('Total: 20'), '20-level report records implemented slice status');

const combined = Object.values(files).join('\n');
check(
  !/3D 已完成|2\.5D 已完成|v6 2\.5D (is )?(complete|completed|finished)|v6 (is )?(complete|completed|finished)/i.test(combined),
  'no stale v6/3D completion claims',
);
check(!/remaining 2D catalog|returns 52|current exposed catalog is 52/i.test(files.readme + files.claude), 'top-level docs do not describe old 52-level runtime');
check(combined.includes('v6 2.5D') && /retired|failed|archiv/i.test(combined), 'v6 2.5D is described as retired/failed/archive context');

console.log('-'.repeat(72));
if (failures) {
  console.error(`${failures} content audit check(s) failed.`);
  process.exit(1);
}
console.log('All content audit checks passed.');
