import { Texture, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import { TideScarWorld } from './tideScarWorld';

describe('Tide Scar canyon presentation', () => {
  it('keeps a separate visible panorama, far mesa, mid/near stack, and 36/26/18 mist presentation layers', () => {
    const world = new TideScarWorld();
    expect(world.root.getObjectByName('tide-scar-far-mesa-cards')).toBeTruthy();
    expect(world.root.getObjectByName('tide-scar-mid-stacks-near-cliff-lips')).toBeTruthy();
    expect(world.root.getObjectByName('tide-scar-far-middle-near-mist-bands')).toBeTruthy();
    expect(world.hasPanorama).toBe(false);
    world.setPanorama(new Texture());
    expect(world.hasPanorama).toBe(true);
    world.update(new Vector3(2, 0, 4), 0, 'portrait');
    expect(world.root.getObjectByName('tide-scar-inward-canyon-panorama')?.position.y).toBe(-67);
  });
});
