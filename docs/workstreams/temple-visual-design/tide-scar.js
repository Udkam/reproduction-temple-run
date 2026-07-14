const canvas = document.querySelector('#world');
const context = canvas.getContext('2d');
const shell = document.querySelector('.relay-shell');
const message = document.querySelector('#world-message');
const reader = document.querySelector('#state-reader');
const pauseButton = document.querySelector('#pause');
if (new URLSearchParams(location.search).has('capture')) shell.classList.add('capture-mode');

const mockStates = {
  'normal-run': { score: 1280, distance: 186, shards: 7, flow: 1, chaseGap: 5.7, obstacle: 'beam', label: 'Normal run' },
  'close-chase': { score: 1484, distance: 242, shards: 8, flow: 1, chaseGap: 1.35, obstacle: 'ring', label: 'Close chase' },
  milestone: { score: 5101, distance: 250, shards: 1, flow: 2, chaseGap: 4.2, obstacle: 'column', milestone: true, label: '250 metre milestone' },
  paused: { score: 1484, distance: 242, shards: 8, flow: 1, chaseGap: 1.35, obstacle: 'gap', paused: true, label: 'Paused run' },
};

let activeKey = 'normal-run';
let activeState = { ...mockStates[activeKey] };
let last = performance.now();
let timeline = 0;
let milestoneTimer = 0;
let fixedPhase = null;

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const { width, height } = canvas.getBoundingClientRect();
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function pointOnRoad(t, width, height) {
  const horizon = height * .255;
  const bottom = height * 1.08;
  const y = horizon + (bottom - horizon) * t;
  const half = (width * .055) + (width * .46) * Math.pow(t, 1.14);
  return { y, half, center: width * .5 };
}

function roadPoint(t, side, width, height) {
  const p = pointOnRoad(t, width, height);
  return { x: p.center + p.half * side, y: p.y };
}

function lerp(a, b, t) { return a + (b - a) * t; }
function drawPoly(points, fill, stroke) {
  context.beginPath();
  points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
  context.closePath();
  if (fill) { context.fillStyle = fill; context.fill(); }
  if (stroke) { context.strokeStyle = stroke; context.stroke(); }
}

function drawWorld(width, height) {
  const deep = context.createLinearGradient(0, 0, 0, height);
  deep.addColorStop(0, '#d9d2c1');
  deep.addColorStop(.25, '#718491');
  deep.addColorStop(.255, '#1b3c53');
  deep.addColorStop(1, '#0d1e2d');
  context.fillStyle = deep;
  context.fillRect(0, 0, width, height);

  context.fillStyle = 'rgba(244,236,216,.42)';
  context.fillRect(0, height * .242, width, 2);
  // Far layer: three quiet mineral silhouettes establish scale without borrowing a temple vocabulary.
  context.fillStyle = 'rgba(28,56,73,.38)';
  for (const [x, scale] of [[.10,.58],[.27,.34],[.73,.36],[.89,.62]]) {
    const base = height * .255; const w = width * .075 * scale; const h = height * .115 * scale;
    drawPoly([{x:width*x-w,y:base},{x:width*x-w*.54,y:base-h*.5},{x:width*x,y:base-h},{x:width*x+w*.63,y:base-h*.35},{x:width*x+w,y:base}], 'rgba(35,67,83,.38)');
  }
  context.fillStyle = 'rgba(244,236,216,.20)';
  for (const [x, h] of [[.18,.065],[.34,.042],[.66,.048],[.82,.076]]) {
    context.fillRect(width*x-width*.002, height*.255-height*h, width*.004, height*h);
  }
  for (let layer = 0; layer < 3; layer += 1) {
    context.fillStyle = `rgba(16,40,60,${.13 + layer * .06})`;
    context.beginPath();
    context.moveTo(0, height * (.28 + layer * .045));
    for (let x = 0; x <= width; x += 36) {
      context.lineTo(x, height * (.29 + layer * .045) + Math.sin((x / width) * 8 + layer) * 7);
    }
    context.lineTo(width, height * (.38 + layer * .06));
    context.lineTo(0, height * (.43 + layer * .06));
    context.closePath();
    context.fill();
  }

  for (const side of [-1, 1]) {
    context.fillStyle = '#183548';
    context.beginPath();
    context.moveTo(width * .5 + side * width * .06, height * .258);
    context.lineTo(width * .5 + side * width * .43, height);
    context.lineTo(width * .5 + side * width * .52, height);
    context.lineTo(width * .5 + side * width * .14, height * .27);
    context.closePath();
    context.fill();
  }

  // Mid layer: tidal pools and a few offset stone masses provide depth and a speed reference.
  for (const [side, t, size] of [[-1,.42,.085],[1,.47,.07],[-1,.60,.12],[1,.64,.10]]) {
    const edge = roadPoint(t, side, width, height);
    context.fillStyle = 'rgba(9,29,44,.52)';
    context.beginPath(); context.ellipse(edge.x + side*width*.075, edge.y + height*.018, width*size, height*size*.15, side*.22, 0, Math.PI*2); context.fill();
    drawPoly([{x:edge.x+side*width*.035,y:edge.y},{x:edge.x+side*width*.105,y:edge.y-height*size*.16},{x:edge.x+side*width*.15,y:edge.y+height*size*.04},{x:edge.x+side*width*.07,y:edge.y+height*size*.12}], 'rgba(52,83,101,.72)');
  }

  const leftTop = roadPoint(0, -1, width, height);
  const rightTop = roadPoint(0, 1, width, height);
  const leftBottom = roadPoint(1, -1, width, height);
  const rightBottom = roadPoint(1, 1, width, height);
  const road = context.createLinearGradient(0, leftTop.y, 0, height);
  road.addColorStop(0, '#aa9470');
  road.addColorStop(1, '#d9c39c');
  drawPoly([leftTop, rightTop, rightBottom, leftBottom], road);

  context.strokeStyle = '#806449';
  context.lineWidth = Math.max(2, width * .003);
  context.beginPath(); context.moveTo(leftTop.x, leftTop.y); context.lineTo(leftBottom.x, leftBottom.y); context.stroke();
  context.beginPath(); context.moveTo(rightTop.x, rightTop.y); context.lineTo(rightBottom.x, rightBottom.y); context.stroke();
  context.strokeStyle = 'rgba(244,236,216,.62)';
  context.lineWidth = 1.25;
  for (const lane of [-1 / 3, 1 / 3]) {
    context.beginPath();
    context.moveTo(width * .5 + lane * (rightTop.x - width * .5), leftTop.y);
    context.lineTo(width * .5 + lane * (rightBottom.x - width * .5), leftBottom.y);
    context.stroke();
  }
  for (const t of [.58, .70, .82]) {
    for (const side of [-1, 1]) {
      const edge = roadPoint(t, side, width, height); const chip = width * (.008 + t*.009);
      drawPoly([{x:edge.x,y:edge.y},{x:edge.x+side*chip,y:edge.y-chip*.16},{x:edge.x+side*chip*1.45,y:edge.y+chip*.12}], '#8f7659');
    }
  }
  drawTideScar(width, height);
}

function drawTideScar(width, height) {
  const close = activeState.chaseGap < 2;
  context.save();
  context.lineCap = 'round';
  context.lineJoin = 'round';
  context.globalAlpha = .62;
  context.strokeStyle = '#f4ecd8';
  context.lineWidth = Math.max(1.15, width * .0019);
  context.beginPath();
  for (let step = 0; step <= 54; step += 1) {
    const t = step / 54;
    const edge = roadPoint(t, 1, width, height);
    const pressure = close ? (1 - t) * 17 : 7;
    const x = edge.x - width * .022 - Math.sin(t * 15 + timeline * .6) * pressure;
    if (step === 0) context.moveTo(x, edge.y); else context.lineTo(x, edge.y);
  }
  context.stroke();
  if (close) {
    context.globalAlpha = .85;
    context.strokeStyle = '#b84432';
    context.lineWidth = Math.max(1.6, width * .0025);
    context.beginPath();
    for (let step = 38; step <= 54; step += 1) {
      const t = step / 54; const edge = roadPoint(t, 1, width, height);
      const x = edge.x - width * .022 - Math.sin(t * 15 + timeline * .6) * 10;
      if (step === 38) context.moveTo(x, edge.y); else context.lineTo(x, edge.y);
    }
    context.stroke();
  }
  context.restore();
}

function drawBeam(width, height, y) {
  const p = pointOnRoad((y - height * .255) / (height * .825), width, height);
  const beamW = p.half * 1.38; const beamH = Math.max(13, height * .022); const left = p.center-beamW/2; const supportW=beamH*.64;
  context.fillStyle = 'rgba(16,40,60,.22)'; context.beginPath(); context.ellipse(p.center, y+beamH*1.18, beamW*.54, beamH*.5, 0, 0, Math.PI*2); context.fill();
  context.fillStyle = '#60412f'; context.fillRect(left, y-beamH, beamW, beamH*1.08);
  context.fillStyle = '#9b7650'; context.fillRect(left, y-beamH, beamW, beamH*.24);
  for (const x of [left-supportW*.18, left+beamW-supportW*.82]) {
    drawPoly([{x,y:y-beamH*.14},{x:x+supportW,y:y-beamH*.14},{x:x+supportW*.82,y:y+beamH*1.65},{x:x+supportW*.18,y:y+beamH*1.65}], '#624833');
    context.fillStyle='#b84432'; context.fillRect(x, y-beamH*.42, supportW, beamH*.28);
  }
}

function drawRing(width, height, y) {
  const p = pointOnRoad((y - height * .255) / (height * .825), width, height);
  const rx = p.half * .72; const ry = Math.max(20, height * .055); const base = y + ry*.35; const thick=Math.max(6,height*.011);
  context.fillStyle='rgba(16,40,60,.2)'; context.beginPath(); context.ellipse(p.center,base+ry*.72,rx*.75,ry*.23,0,0,Math.PI*2); context.fill();
  context.save(); context.strokeStyle = '#60412f'; context.lineWidth = thick;
  context.beginPath(); context.ellipse(p.center, base, rx, ry, 0, Math.PI, 0); context.stroke();
  context.strokeStyle = '#b79770'; context.lineWidth = Math.max(2, thick*.28);
  context.beginPath(); context.ellipse(p.center, base-thick*.18, rx-thick*.22, ry-thick*.24, 0, Math.PI, 0); context.stroke();
  context.strokeStyle = '#b84432'; context.lineWidth = Math.max(3, thick*.34);
  context.beginPath(); context.moveTo(p.center-rx,base); context.lineTo(p.center-rx,base+ry*.86); context.moveTo(p.center+rx,base); context.lineTo(p.center+rx,base+ry*.86); context.stroke(); context.restore();
}

function drawColumn(width, height, y) {
  const p = pointOnRoad((y - height * .255) / (height * .825), width, height); const size = Math.max(28, p.half * .34); const h = size * 2.28;
  context.fillStyle='rgba(16,40,60,.24)'; context.beginPath(); context.ellipse(p.center,y+size*.09,size*.78,size*.20,0,0,Math.PI*2); context.fill();
  drawPoly([{x:p.center-size*.62,y:y},{x:p.center+size*.52,y:y-size*.1},{x:p.center+size*.32,y:y-h},{x:p.center-size*.36,y:y-h*.88}], '#75614d', '#14202b');
  drawPoly([{x:p.center+size*.52,y:y-size*.1},{x:p.center+size*.32,y:y-h},{x:p.center+size*.72,y:y-h*.74},{x:p.center+size*.9,y:y-size*.02}], '#29495e');
  drawPoly([{x:p.center-size*.62,y:y},{x:p.center-size*.36,y:y-h*.88},{x:p.center-size*.05,y:y-h*.54},{x:p.center-size*.15,y:y-size*.03}], '#b89871');
  context.fillStyle = '#b84432'; context.fillRect(p.center - size * .22, y - h * .93, size * .5, Math.max(5, size * .13));
}

function drawGap(width, height, y) {
  const t = (y - height * .255) / (height * .825); const near = pointOnRoad(t, width, height); const far = pointOnRoad(Math.max(0, t - .105), width, height);
  drawPoly([{x:near.center-near.half,y},{x:near.center+near.half,y},{x:far.center+far.half,y:far.y},{x:far.center-far.half,y:far.y}], '#0d1e2d');
  context.strokeStyle = '#b84432'; context.lineWidth = Math.max(4, height*.007);
  context.beginPath(); context.moveTo(near.center-near.half,y); context.lineTo(near.center+near.half,y); context.stroke();
  context.strokeStyle = '#f4ecd8'; context.lineWidth = Math.max(2, height*.0035);
  context.beginPath(); context.moveTo(far.center-far.half,far.y); context.lineTo(far.center+far.half,far.y); context.stroke();
  context.fillStyle = '#8f7659';
  for (const side of [-1,1]) drawPoly([{x:near.center+side*near.half,y},{x:near.center+side*(near.half+width*.035),y:y-height*.012},{x:near.center+side*(near.half+width*.018),y:y+height*.025}], '#8f7659');
}

function drawObstacle(width, height) {
  const y = height * (height / width > 1.35 ? .45 : .43);
  if (activeState.obstacle === 'beam') drawBeam(width, height, y);
  if (activeState.obstacle === 'ring') drawRing(width, height, y);
  if (activeState.obstacle === 'column') drawColumn(width, height, y);
  if (activeState.obstacle === 'gap') drawGap(width, height, y);
}

function limb(start, elbow, foot, widths, color) {
  context.strokeStyle = color; context.lineCap = 'round';
  context.lineWidth = widths[0]; context.beginPath(); context.moveTo(start.x,start.y); context.lineTo(elbow.x,elbow.y); context.stroke();
  context.lineWidth = widths[1]; context.beginPath(); context.moveTo(elbow.x,elbow.y); context.lineTo(foot.x,foot.y); context.stroke();
}

function drawRunner(width, height) {
  const portrait = height / width > 1.3; const baseX = width * .5; const baseY = height * (portrait ? .70 : .68); const unit = Math.min(width, height) * (portrait ? .20 : .13);
  const phase = (timeline % .42) / .42; const lead = Math.cos(phase * Math.PI * 2); const compression = Math.abs(lead) * unit*.042;
  context.save(); context.translate(baseX, baseY); context.rotate(-.12); context.fillStyle = 'rgba(13,30,45,.27)'; context.beginPath(); context.ellipse(0, unit*.63, unit*.42, unit*.12, .12, 0, Math.PI*2); context.fill();
  const pelvisY = unit*.06 + compression; const hipL={x:-unit*.12,y:pelvisY}; const hipR={x:unit*.12,y:pelvisY};
  const footL={x:-unit*(.08+Math.max(0,-lead)*.30),y:unit*(.65-Math.max(0,-lead)*.13)};
  const footR={x:unit*(.08+Math.max(0,lead)*.30),y:unit*(.65-Math.max(0,lead)*.13)};
  const kneeL={x:(hipL.x+footL.x)*.5-unit*.035,y:unit*(.34+Math.max(0,-lead)*.07)+compression};
  const kneeR={x:(hipR.x+footR.x)*.5+unit*.035,y:unit*(.34+Math.max(0,lead)*.07)+compression};
  limb(hipL,kneeL,footL,[unit*.15,unit*.12],'#172c3e'); limb(hipR,kneeR,footR,[unit*.15,unit*.12],'#243d52');
  drawPoly([{x:-unit*.25,y:-unit*.49+compression},{x:unit*.25,y:-unit*.49+compression},{x:unit*.29,y:pelvisY+unit*.06},{x:0,y:pelvisY+unit*.14},{x:-unit*.29,y:pelvisY+unit*.06}], '#e7d6b4', '#14202b');
  context.fillStyle='#b84432'; context.fillRect(-unit*.22,-unit*.45+compression,unit*.07,unit*.46);
  const shoulderL={x:-unit*.23,y:-unit*.42+compression}; const shoulderR={x:unit*.23,y:-unit*.42+compression};
  const elbowL={x:-unit*(.31-lead*.05),y:-unit*.18+compression}; const handL={x:-unit*(.37-lead*.07),y:unit*(.01-Math.max(0,lead)*.10)+compression};
  const elbowR={x:unit*(.31+lead*.05),y:-unit*.18+compression}; const handR={x:unit*(.37+lead*.07),y:unit*(.01-Math.max(0,-lead)*.10)+compression};
  limb(shoulderL,elbowL,handL,[unit*.11,unit*.09],'#31536b'); limb(shoulderR,elbowR,handR,[unit*.11,unit*.09],'#31536b');
  context.fillStyle='#14202b'; context.beginPath(); context.arc(0,-unit*.69+compression,unit*.18,0,Math.PI*2); context.fill();
  context.restore();
}

function drawPursuer(width, height) {
  const portrait = height / width > 1.3; const closeT = Math.max(0, Math.min(1, (5.7-activeState.chaseGap)/5.05)); const y=lerp(height*(portrait ? .95 : .94),height*(portrait ? .90 : .915),closeT); const x=width*.5+Math.sin(timeline*5)*width*.006; const size=lerp(Math.min(width,height)*(portrait ? .13 : .10),Math.min(width,height)*(portrait ? .20 : .16),closeT);
  context.save(); context.translate(x,y); context.fillStyle='rgba(13,30,45,.29)'; context.beginPath(); context.ellipse(0,size*.28,size*.88,size*.17,0,0,Math.PI*2); context.fill();
  for (const side of [-1,1]) { const bob=Math.sin(timeline*17+(side>0?Math.PI:0))*size*.035; limb({x:side*size*.29,y:-size*.06},{x:side*size*.52,y:size*.13+bob},{x:side*size*.46,y:size*.31},[size*.12,size*.1],'#0b1722'); }
  drawPoly([{x:-size*.48,y:-size*.05},{x:-size*.30,y:-size*.44},{x:0,y:-size*.53},{x:size*.30,y:-size*.44},{x:size*.48,y:-size*.05},{x:size*.25,y:size*.18},{x:-size*.25,y:size*.18}], '#18364c', '#31536b');
  context.fillStyle='#0d2639'; context.beginPath(); context.arc(0,-size*.62,size*.18,0,Math.PI*2); context.fill();
  context.fillStyle='#b84432'; context.fillRect(-size*.05,-size*.45,size*.10,size*.34);
  for (const side of [-1,1]) limb({x:side*size*.20,y:-size*.25},{x:side*size*.39,y:size*.02},{x:side*size*.31,y:size*.30},[size*.13,size*.1],'#294d66');
  context.restore();
}

function paint() {
  const { width, height } = canvas.getBoundingClientRect();
  context.clearRect(0, 0, width, height);
  drawWorld(width, height); drawObstacle(width, height); drawRunner(width, height); drawPursuer(width, height);
  if (activeState.paused) { context.fillStyle = 'rgba(13,30,45,.22)'; context.fillRect(0,0,width,height); }
}

function clippedBounds(box, width, height) {
  const left = Math.max(0, box.left); const top = Math.max(0, box.top);
  const right = Math.min(width, box.right); const bottom = Math.min(height, box.bottom);
  return { left, top, right, bottom, width: Math.max(0, right-left), height: Math.max(0, bottom-top), area: Math.max(0, right-left) * Math.max(0, bottom-top) };
}

function luminance(hex) {
  const channels = hex.match(/[a-f0-9]{2}/gi).map(value => parseInt(value, 16) / 255).map(value => value <= .04045 ? value / 12.92 : Math.pow((value + .055) / 1.055, 2.4));
  return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
}

function diagnostics() {
  const { width, height } = canvas.getBoundingClientRect(); const portrait = height / width > 1.3; const unit = Math.min(width,height) * (portrait ? .20 : .13); const runnerY = height * (portrait ? .70 : .68);
  const closeT = Math.max(0, Math.min(1, (5.7 - activeState.chaseGap) / 5.05)); const pursuerY = lerp(height*(portrait ? .95 : .94),height*(portrait ? .90 : .915),closeT); const pursuerSize = lerp(Math.min(width,height)*(portrait ? .13 : .10),Math.min(width,height)*(portrait ? .20 : .16),closeT); const obstacleY = height * (height / width > 1.35 ? .45 : .43); const p = pointOnRoad((obstacleY-height*.255)/(height*.825), width, height);
  const obstacle = activeState.obstacle === 'beam' ? { left:p.center-p.half*.78, top:obstacleY-Math.max(12,height*.018)*1.2, right:p.center+p.half*.78, bottom:obstacleY+Math.max(12,height*.018) } : activeState.obstacle === 'ring' ? { left:p.center-p.half*.82, top:obstacleY-Math.max(18,height*.048), right:p.center+p.half*.82, bottom:obstacleY+Math.max(18,height*.048) } : activeState.obstacle === 'column' ? { left:p.center-p.half*.35, top:obstacleY-p.half*.7, right:p.center+p.half*.35, bottom:obstacleY+2 } : { left:p.center-p.half, top:obstacleY-height*.005, right:p.center+p.half, bottom:obstacleY+height*.085 };
  const contrast = (a,b) => { const [high,low] = [luminance(a),luminance(b)].sort((x,y)=>y-x); return Number(((high+.05)/(low+.05)).toFixed(2)); };
  const runner = clippedBounds({left:width*.5-unit*.62,top:runnerY-unit*.92,right:width*.5+unit*.62,bottom:runnerY+unit*.75},width,height); const pursuer = clippedBounds({left:width*.5-pursuerSize*.65,top:pursuerY-pursuerSize*.82,right:width*.5+pursuerSize*.65,bottom:pursuerY+pursuerSize*.38},width,height);
  return { state: activeKey, mockState:{...activeState}, canvasCount:1, gameplayDomEntities:document.querySelectorAll('[data-world-entity]').length, overflowX:Math.max(0, document.documentElement.scrollWidth-window.innerWidth), hud:Array.from(document.querySelectorAll('.hud, .pause-button')).map(item => { const r=item.getBoundingClientRect(); return { selector:item.className || item.id, left:r.left,top:r.top,right:r.right,bottom:r.bottom }; }), runner, pursuer, pursuerGapPx:Number((pursuer.top-runner.bottom).toFixed(2)), obstacle:{kind:activeState.obstacle,bounds:clippedBounds(obstacle,width,height)}, contrast:{hudOnSky:contrast('#14202b','#e7d6b4'), scarOnTide:contrast('#f4ecd8','#10283c'), coralOnSand:contrast('#b84432','#e7d6b4')}, reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches };
}

function updateHud() {
  document.querySelector('#score').textContent = activeState.score.toLocaleString('en-US');
  document.querySelector('#distance').textContent = activeState.distance;
  document.querySelector('#flow').textContent = `×${activeState.flow}`;
  document.querySelector('#shards').textContent = activeState.shards;
  pauseButton.setAttribute('aria-pressed', String(Boolean(activeState.paused)));
  pauseButton.textContent = activeState.paused ? '▶' : 'Ⅱ';
  reader.textContent = `${activeState.label}; score ${activeState.score}; distance ${activeState.distance} metres; flow ${activeState.flow}; shards ${activeState.shards}.`;
}

function setState(key) {
  activeKey = key; activeState = { ...mockStates[key] }; milestoneTimer = activeState.milestone ? 800 : 0;
  shell.classList.toggle('chase-close', activeState.chaseGap < 2 && !activeState.paused);
  document.querySelectorAll('[data-state]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.state === key)));
  document.querySelectorAll('[data-obstacle]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.obstacle === activeState.obstacle)));
  updateHud();
  if (activeState.milestone) { message.textContent = '250 m'; message.classList.remove('visible'); void message.offsetWidth; message.classList.add('visible'); } else { message.classList.remove('visible'); }
}

document.querySelectorAll('[data-state]').forEach(button => button.addEventListener('click', () => setState(button.dataset.state)));
document.querySelectorAll('[data-obstacle]').forEach(button => button.addEventListener('click', () => { activeState.obstacle = button.dataset.obstacle; document.querySelectorAll('[data-obstacle]').forEach(item => item.setAttribute('aria-pressed', String(item === button))); reader.textContent = `${activeState.obstacle} silhouette preview.`; }));
pauseButton.addEventListener('click', () => setState(activeState.paused ? 'normal-run' : 'paused'));
window.addEventListener('keydown', event => { const states = ['normal-run','close-chase','milestone','paused']; const obstacles = ['beam','ring','column','gap']; if (/^[1-4]$/.test(event.key)) setState(states[Number(event.key)-1]); if (/^[5-8]$/.test(event.key)) { activeState.obstacle=obstacles[Number(event.key)-5]; updateHud(); } });

function loop(now) {
  const elapsed = Math.min(50, now - last); last = now;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (fixedPhase !== null) timeline = fixedPhase * .42;
  else if (!activeState.paused && !reduce) timeline += elapsed / 1000;
  if (reduce && fixedPhase === null) timeline = Math.floor(now / 166) * .166;
  if (milestoneTimer > 0) { milestoneTimer -= elapsed; if (milestoneTimer <= 0) message.classList.remove('visible'); }
  paint(); requestAnimationFrame(loop);
}

resize(); updateHud(); requestAnimationFrame(loop); addEventListener('resize', resize);
window.__tideScarDiagnostics = diagnostics;
window.__tideScarSetPhase = (phase) => { fixedPhase = Math.max(0, Math.min(.999, phase)); timeline = fixedPhase * .42; paint(); };
window.__tideScarResumePhase = () => { fixedPhase = null; };
window.__tideScarSetState = setState;
window.__tideScarSetObstacle = (obstacle) => { activeState.obstacle = obstacle; updateHud(); };
