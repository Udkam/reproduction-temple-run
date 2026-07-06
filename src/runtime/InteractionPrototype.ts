export interface InteractionPrototypeOptions {
  onToggleRecursiveSpace: () => void;
}

export class InteractionPrototype {
  private enabled = false;
  private readonly handleKeyDown = (event: KeyboardEvent) => {
    if (event.repeat || event.key.toLowerCase() !== "e") {
      return;
    }

    event.preventDefault();
    this.options.onToggleRecursiveSpace();
  };

  constructor(private readonly options: InteractionPrototypeOptions) {}

  start() {
    if (this.enabled) {
      return;
    }

    window.addEventListener("keydown", this.handleKeyDown);
    this.enabled = true;
  }

  destroy() {
    if (!this.enabled) {
      return;
    }

    window.removeEventListener("keydown", this.handleKeyDown);
    this.enabled = false;
  }
}
