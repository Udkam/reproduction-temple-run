import type {
  EntityProjection,
  PrototypeWorldGraph,
  WorldAddress,
  WorldId,
  WorldProjection,
} from "./types";

const STAGE2_PROTOTYPE_GRAPH: PrototypeWorldGraph = {
  rootWorldId: "world-a",
  worlds: {
    "world-a": {
      id: "world-a",
      paletteId: "void-lab",
      size: { width: 10, height: 8 },
    },
    "world-c": {
      id: "world-c",
      paletteId: "inner-mint",
      size: { width: 8, height: 6 },
    },
  },
  entities: [
    {
      id: "player-a",
      kind: "player",
      worldId: "world-a",
      bounds: { x: 2.1, y: 2.1, width: 1.25, height: 1.25 },
    },
    {
      id: "box-a",
      kind: "box",
      worldId: "world-a",
      bounds: { x: 5.75, y: 2.1, width: 1.25, height: 1.25 },
    },
    {
      id: "container-b",
      kind: "recursive-container",
      worldId: "world-a",
      bounds: { x: 5.35, y: 4.35, width: 1.75, height: 1.75 },
      innerWorldId: "world-c",
    },
    {
      id: "goal-a",
      kind: "goal",
      worldId: "world-a",
      bounds: { x: 1.1, y: 5.25, width: 1.25, height: 1.25 },
    },
    {
      id: "goal-c",
      kind: "goal",
      worldId: "world-c",
      bounds: { x: 1.0, y: 1.0, width: 1.3, height: 1.3 },
    },
    {
      id: "box-c",
      kind: "box",
      worldId: "world-c",
      bounds: { x: 4.65, y: 3.2, width: 1.35, height: 1.35 },
    },
  ],
};

export function createRecursiveInteractionProjection(maxDepth = 2) {
  return projectWorldGraph(STAGE2_PROTOTYPE_GRAPH, STAGE2_PROTOTYPE_GRAPH.rootWorldId, maxDepth);
}

export const createStage2Projection = createRecursiveInteractionProjection;

export function projectWorldGraph(
  graph: PrototypeWorldGraph,
  rootWorldId: WorldId,
  maxDepth: number,
): WorldProjection {
  const rootAddress: WorldAddress = { rootWorldId, path: [] };
  return projectWorld(graph, rootWorldId, rootAddress, 0, maxDepth);
}

function projectWorld(
  graph: PrototypeWorldGraph,
  worldId: WorldId,
  address: WorldAddress,
  depth: number,
  maxDepth: number,
): WorldProjection {
  const world = graph.worlds[worldId];
  if (!world) {
    throw new Error(`Projection references unknown world "${worldId}".`);
  }

  const entities: EntityProjection[] = graph.entities
    .filter((entity) => entity.worldId === worldId)
    .map((entity) => {
      if (entity.kind !== "recursive-container" || !entity.innerWorldId || depth >= maxDepth) {
        return { entity };
      }

      return {
        entity,
        childWorld: projectWorld(
          graph,
          entity.innerWorldId,
          { rootWorldId: address.rootWorldId, path: [...address.path, entity.id] },
          depth + 1,
          maxDepth,
        ),
      };
    });

  return {
    projectionId: [worldId, ...address.path].join(":"),
    world,
    address,
    depth,
    entities,
  };
}
