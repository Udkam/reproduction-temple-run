export type WorldId = string;
export type EntityId = string;
export type PaletteId = "void-lab" | "inner-mint";

export interface Size2D {
  width: number;
  height: number;
}

export interface Rect2D {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface WorldAddress {
  rootWorldId: WorldId;
  path: EntityId[];
}

export interface PrototypeWorld {
  id: WorldId;
  paletteId: PaletteId;
  size: Size2D;
}

export type PrototypeEntityKind = "player" | "box" | "recursive-container" | "goal";

export interface PrototypeEntity {
  id: EntityId;
  kind: PrototypeEntityKind;
  worldId: WorldId;
  bounds: Rect2D;
  innerWorldId?: WorldId;
}

export interface PrototypeWorldGraph {
  rootWorldId: WorldId;
  worlds: Record<WorldId, PrototypeWorld>;
  entities: PrototypeEntity[];
}

export interface EntityProjection {
  entity: PrototypeEntity;
  childWorld?: WorldProjection;
}

export interface WorldProjection {
  projectionId: string;
  world: PrototypeWorld;
  address: WorldAddress;
  depth: number;
  entities: EntityProjection[];
}
