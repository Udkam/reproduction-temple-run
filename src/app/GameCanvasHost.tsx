import { useEffect, useRef } from "react";
import { GameRuntime } from "../runtime/GameRuntime";

export function GameCanvasHost() {
  const hostRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) {
      return;
    }

    const runtime = new GameRuntime(host);
    void runtime.start();

    return () => {
      runtime.destroy();
    };
  }, []);

  return (
    <main className="app-shell" aria-label="Recursive box study">
      <div className="stage-frame">
        <div ref={hostRef} className="pixi-stage-host" data-testid="pixi-stage-host" />
      </div>
    </main>
  );
}
