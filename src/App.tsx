import { useEffect, useMemo, useRef, useState } from 'react';
import { getCurrentSection, isTurnWindow, type FailureReason } from './game/core';
import type { RunnerAction } from './game/input/InputController';
import { GameRuntime, type RuntimeOptions, type RuntimeSnapshot } from './game/runtime/GameRuntime';

const RECORD_KEY = 'tide-relay.best-distance';
const SCORE_KEY = 'tide-relay.best-score';
const AUDIO_KEY = 'tide-relay.audio';
const CONTRAST_KEY = 'tide-relay.high-contrast';

function readBoolean(key: string, fallback: boolean): boolean {
  try {
    const value = window.localStorage.getItem(key);
    return value === null ? fallback : value === 'true';
  } catch {
    return fallback;
  }
}

function readBest(): number {
  try {
    const value = Number(window.localStorage.getItem(RECORD_KEY));
    return Number.isFinite(value) && value > 0 ? value : 0;
  } catch {
    return 0;
  }
}

function readBestScore(): number {
  try {
    const value = Number(window.localStorage.getItem(SCORE_KEY));
    return Number.isFinite(value) && value > 0 ? Math.floor(value) : 0;
  } catch {
    return 0;
  }
}

function describeFailure(reason: FailureReason | null): string {
  if (!reason) return 'The meridian signal was lost.';
  if (reason.kind === 'wrong-turn') return `Wrong turn — relay expected ${reason.expected}.`;
  if (reason.kind === 'missed-turn') return `Missed ${reason.expected} turn window.`;
  if (reason.kind === 'gap-fall') return 'The causeway collapsed beneath the relay.';
  if (reason.kind === 'pursuer-caught') return 'The black tide caught you.';
  return `Impact detected: ${reason.hazard}.`;
}

function formatDistance(value: number): string {
  return Math.floor(value).toLocaleString('en-US');
}

export default function App() {
  const hostRef = useRef<HTMLDivElement>(null);
  const runtimeRef = useRef<GameRuntime | null>(null);
  const [snapshot, setSnapshot] = useState<RuntimeSnapshot | null>(null);
  const [audioEnabled, setAudioEnabled] = useState(() => readBoolean(AUDIO_KEY, true));
  const [highContrast, setHighContrast] = useState(() => readBoolean(CONTRAST_KEY, false));
  const [reducedMotion] = useState(() => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false);
  const [bestDistance, setBestDistance] = useState(readBest);
  const [bestScore, setBestScore] = useState(readBestScore);

  const options = useMemo<RuntimeOptions>(() => ({
    seed: 0x54494445,
    audioEnabled,
    highContrast,
    reducedMotion,
  }), [audioEnabled, highContrast, reducedMotion]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const runtime = new GameRuntime(options);
    runtimeRef.current = runtime;
    const unsubscribe = runtime.subscribe(setSnapshot);
    let disposed = false;
    void runtime.init(host).catch((error: unknown) => {
      if (!disposed) console.error('TIDE//RELAY failed to initialize', error);
    });
    return () => {
      disposed = true;
      unsubscribe();
      runtime.destroy();
      if (runtimeRef.current === runtime) runtimeRef.current = null;
    };
    // Runtime lifecycle is intentionally mount-bound. Options update through setOptions.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    runtimeRef.current?.setOptions(options);
    try {
      window.localStorage.setItem(AUDIO_KEY, String(audioEnabled));
      window.localStorage.setItem(CONTRAST_KEY, String(highContrast));
    } catch {
      // Storage is optional; gameplay remains available in privacy-restricted contexts.
    }
  }, [options, audioEnabled, highContrast]);

  const state = snapshot?.state;
  useEffect(() => {
    if (!state || state.status !== 'game-over') return;
    const nextDistance = Math.max(bestDistance, state.distance);
    const nextScore = Math.max(bestScore, state.score);
    if (nextDistance !== bestDistance) setBestDistance(nextDistance);
    if (nextScore !== bestScore) setBestScore(nextScore);
    try {
      window.localStorage.setItem(RECORD_KEY, String(nextDistance));
      window.localStorage.setItem(SCORE_KEY, String(nextScore));
    } catch {
      // Record persistence is optional.
    }
  }, [state, bestDistance, bestScore]);

  const focusCanvas = () => requestAnimationFrame(() => hostRef.current?.querySelector('canvas')?.focus());
  const start = () => {
    runtimeRef.current?.start();
    focusCanvas();
  };
  const resume = () => {
    runtimeRef.current?.resume();
    focusCanvas();
  };
  const restart = () => {
    runtimeRef.current?.restart();
    focusCanvas();
  };
  const action = (value: RunnerAction) => {
    runtimeRef.current?.action(value);
    focusCanvas();
  };
  const toggleAudio = () => {
    const next = !audioEnabled;
    runtimeRef.current?.setOptions({ audioEnabled: next });
    if (next) runtimeRef.current?.primeAudio();
    setAudioEnabled(next);
  };

  const status = state?.status ?? 'ready';
  const hudScore = Math.floor(state?.score ?? 0);
  const hudDistance = Math.floor(state?.distance ?? 0);
  const hudShards = state?.shards ?? 0;
  const hudFlow = state?.multiplier ?? 1;
  const section = state ? getCurrentSection(state) : null;
  const milestoneMeters = Math.floor((state?.distance ?? 0) / 250) * 250;
  const showMilestone = Boolean(
    state?.status === 'running' &&
    milestoneMeters > 0 &&
    state.distance - milestoneMeters < Math.max(12, state.speed * 1.15),
  );
  const turnWindowActive = Boolean(state && isTurnWindow(state));
  const showTurnCue = Boolean(
    state &&
    section &&
    state.status === 'running' &&
    state.sectionDistance >= section.turnWarningStart,
  );
  const liveMessage = status === 'game-over'
    ? describeFailure(state?.failureReason ?? null)
    : status === 'paused'
      ? 'Relay paused.'
      : turnWindowActive && section
        ? `${section.requiredTurn} turn now.`
        : '';

  return (
    <main className={`app${highContrast ? ' is-high-contrast' : ''}${status === 'running' ? ' is-running' : ''}${status === 'paused' ? ' is-paused' : ''}${status === 'game-over' ? ' is-game-over' : ''}`} id="game">
      <a className="skip-link" href="#primary-action">Skip to game controls</a>
      <div ref={hostRef} className="world-host" data-testid="world-host" />

      <header className="brandbar" aria-label="Tide Relay">
        <span className="brand-glyph" aria-hidden="true"><i /></span>
        <span className="brand-copy"><strong>Tide Relay</strong><span>follow the tide scar</span></span>
      </header>

      <section className="hud" aria-label="Run status" data-score={hudScore} data-distance={hudDistance} data-shards={hudShards} data-flow={hudFlow}>
        <div className="metric metric--score"><span>Score</span><strong>{hudScore.toLocaleString('en-US')}</strong></div>
        <div className="metric metric--distance"><span>Distance</span><strong>{hudDistance.toLocaleString('en-US')} <small>m</small></strong></div>
        <div className="metric metric--flow"><span>Flow</span><strong>×{hudFlow}</strong></div>
        <div className="metric metric--shards"><span>Shards</span><strong>{hudShards}</strong></div>
      </section>

      {showMilestone ? (
        <div className="distance-milestone" aria-hidden="true">
          <span>still running</span><strong>{milestoneMeters.toLocaleString('en-US')} m</strong>
        </div>
      ) : null}

      <button
        className="pause-control"
        type="button"
        aria-label={status === 'paused' ? 'Resume' : 'Pause'}
        disabled={status === 'ready' || status === 'game-over'}
        onClick={() => status === 'paused' ? resume() : runtimeRef.current?.pause()}
      >{status === 'paused' ? '▶' : 'Ⅱ'}</button>

      {status === 'paused' ? <p className="pause-marker" role="status">Paused</p> : null}

      {showTurnCue && section ? (
        <div className={`turn-cue${turnWindowActive ? '' : ' turn-cue--warning'}`} data-testid="turn-cue">
          <strong aria-hidden="true">{section.requiredTurn === 'left' ? '←' : '→'}</strong>
          <span>{turnWindowActive ? 'turn now' : 'path bends'} {section.requiredTurn}</span>
        </div>
      ) : null}

      {(state?.runner.shieldCharges ?? 0) > 0 ? <div className="shield-rail" aria-label="Aegis charge ready"><i /></div> : null}

      {status !== 'running' && status !== 'paused' ? (
        <section className="overlay" aria-modal="true" role="dialog" aria-labelledby="overlay-title">
          <div className="overlay-card">
            {status === 'ready' ? (
              <>
                <p className="overlay-eyebrow">the path remembers every footstep</p>
                <h1 id="overlay-title">Tide<br /><em>Relay</em></h1>
                <p className="overlay-copy">Run the flooded observatory. Use arrows or one-finger swipes to read the ruins, jump broken spans, duck beneath instruments—and do not let the tide catch you.</p>
                <div className="ready-meta">
                  <p><span>best distance</span><strong>{formatDistance(bestDistance)} m</strong></p>
                  <p><span>best score</span><strong>{bestScore.toLocaleString('en-US')}</strong></p>
                  <p><span>move</span><strong>arrows / swipe</strong></p>
                </div>
                <div className="overlay-actions"><button id="primary-action" className="primary-action" type="button" onClick={start}>Start running</button></div>
              </>
            ) : (
              <>
                <p className="overlay-eyebrow">the tide caught up</p>
                <h2 id="overlay-title">Run<br />ended</h2>
                <p className="failure-reason">{describeFailure(state?.failureReason ?? null)}</p>
                <div className="ready-meta ready-meta--results">
                  <p><span>distance</span><strong>{formatDistance(state?.distance ?? 0)} m</strong></p>
                  <p><span>best</span><strong>{formatDistance(Math.max(bestDistance, state?.distance ?? 0))} m</strong></p>
                  <p><span>score</span><strong>{Math.floor(state?.score ?? 0).toLocaleString('en-US')}</strong></p>
                  <p><span>shards</span><strong>{state?.shards ?? 0}</strong></p>
                </div>
                <div className="overlay-actions"><button id="primary-action" className="primary-action" type="button" onClick={restart}>Run again</button></div>
              </>
            )}
          </div>
        </section>
      ) : null}

      <nav className="touch-controls" aria-label="Runner controls">
        <button className="touch-action" type="button" aria-label="Move or turn left" disabled={status !== 'running'} onClick={() => action('left')}>←</button>
        <button className="touch-action" type="button" aria-label="Jump" disabled={status !== 'running'} onClick={() => action('jump')}>↑</button>
        <button className="touch-action" type="button" aria-label="Slide" disabled={status !== 'running'} onClick={() => action('slide')}>↓</button>
        <button className="touch-action" type="button" aria-label="Move or turn right" disabled={status !== 'running'} onClick={() => action('right')}>→</button>
      </nav>
      {status === 'running' && (state?.distance ?? 0) < 20 ? <p className="gesture-hint">swipe sideways · up to jump · down to slide</p> : null}

      <div className="settings" aria-label="Presentation settings">
        <button className="setting-button" type="button" aria-pressed={audioEnabled} onClick={toggleAudio}>sound</button>
        <button className="setting-button" type="button" aria-pressed={highContrast} onClick={() => setHighContrast((value) => !value)}>contrast</button>
      </div>
      <p className="sr-only" aria-live="polite">{liveMessage}</p>
    </main>
  );
}
