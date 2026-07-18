import { Texture } from 'three';
import { describe, expect, it } from 'vitest';
import {
  D4_MOBILE_ENVIRONMENT_BYTES,
  loadD4Assets,
  selectD4Assets,
  shouldUseD4MobileTier,
} from './d4Assets';

describe('D4 asset preselection and lifecycle', () => {
  it('selects exactly one pre-upload tier and the approved mobile memory budget', () => {
    const mobile = selectD4Assets({ cssWidth: 390, cssHeight: 844, deviceMemory: 8 });
    expect(mobile.tier).toBe('mobile');
    expect(mobile.requestedFiles).toEqual([
      'tide-sandstone-base-mobile-512.webp',
      'tide-basalt-base-mobile-512.webp',
      'tide-distant-canyon-mobile-1024x512.webp',
      'tide-coral-mask-512.png',
    ]);
    expect(mobile.textureBytes).toBe(D4_MOBILE_ENVIRONMENT_BYTES);
    expect(selectD4Assets({ cssWidth: 1440, cssHeight: 900 }).tier).toBe('desktop');
    expect(shouldUseD4MobileTier({ cssWidth: 844, cssHeight: 390, coarsePointer: true })).toBe(true);
  });

  it('sets sRGB/no-color-space, degrades without blocking, and disposes a late loaded set once', async () => {
    const textures = [new Texture(), new Texture(), new Texture(), new Texture()];
    const assetSet = await loadD4Assets(
      { cssWidth: 1440, cssHeight: 900 },
      () => ({ loadAsync: async () => textures.shift()! }),
    );
    expect(assetSet.fallback).toBe(false);
    expect(assetSet.textures?.sandstone.colorSpace).toBe('srgb');
    expect(assetSet.textures?.coral.colorSpace).toBe('');
    const dispose = assetSet.textures?.sandstone.dispose;
    let disposed = 0;
    assetSet.textures?.sandstone.addEventListener('dispose', () => { disposed += 1; });
    assetSet.dispose();
    assetSet.dispose();
    expect(dispose).toBeTypeOf('function');
    expect(disposed).toBe(1);

    const fallback = await loadD4Assets({ cssWidth: 390, cssHeight: 844 }, () => ({ loadAsync: async () => { throw new Error('offline'); } }));
    expect(fallback.fallback).toBe(true);
    expect(fallback.textures).toBeNull();
  });
});
