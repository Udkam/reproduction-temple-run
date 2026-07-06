import { createStage2Projection } from "../projection/worldProjection";
import { PixiApp } from "../render/PixiApp";

export class GameRuntime {
  private readonly host: HTMLElement;
  private pixiApp: PixiApp | null = null;
  private destroyed = false;

  constructor(host: HTMLElement) {
    this.host = host;
  }

  async start() {
    const pixiApp = new PixiApp(this.host);
    await pixiApp.init();

    if (this.destroyed) {
      pixiApp.destroy();
      return;
    }

    this.pixiApp = pixiApp;
    this.pixiApp.render(createStage2Projection());
  }

  destroy() {
    this.destroyed = true;

    if (!this.pixiApp) {
      return;
    }

    this.pixiApp.destroy();
    this.pixiApp = null;
  }
}
