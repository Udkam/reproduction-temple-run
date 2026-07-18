import { NoColorSpace, RepeatWrapping, SRGBColorSpace, Texture, TextureLoader } from 'three';

export type D4AssetTier = 'desktop' | 'mobile';

export interface D4AssetCapabilities {
  cssWidth: number;
  cssHeight: number;
  deviceMemory?: number;
  coarsePointer?: boolean;
}

export interface D4AssetRecord {
  file: string;
  rgba8MipBytes: number;
  colorSpace: 'srgb' | 'none';
}

export interface D4AssetSelection {
  tier: D4AssetTier;
  sandstone: D4AssetRecord;
  basalt: D4AssetRecord;
  canyon: D4AssetRecord;
  coral: D4AssetRecord;
  requestedFiles: readonly string[];
  textureBytes: number;
}

export interface D4LoadedAssets extends D4AssetSelection {
  fallback: boolean;
  textures: { sandstone: Texture; basalt: Texture; canyon: Texture; coral: Texture } | null;
  dispose(): void;
}

export interface D4TextureLoader {
  loadAsync(url: string): Promise<Texture>;
}

const DESKTOP = {
  sandstone: { file: 'tide-sandstone-base-1024.webp', rgba8MipBytes: 5_592_404, colorSpace: 'srgb' },
  basalt: { file: 'tide-basalt-base-1024.webp', rgba8MipBytes: 5_592_404, colorSpace: 'srgb' },
  canyon: { file: 'tide-distant-canyon-2048x1024.webp', rgba8MipBytes: 11_184_812, colorSpace: 'srgb' },
} as const satisfies Record<'sandstone' | 'basalt' | 'canyon', D4AssetRecord>;

const MOBILE = {
  sandstone: { file: 'tide-sandstone-base-mobile-512.webp', rgba8MipBytes: 1_398_100, colorSpace: 'srgb' },
  basalt: { file: 'tide-basalt-base-mobile-512.webp', rgba8MipBytes: 1_398_100, colorSpace: 'srgb' },
  canyon: { file: 'tide-distant-canyon-mobile-1024x512.webp', rgba8MipBytes: 2_796_204, colorSpace: 'srgb' },
} as const satisfies Record<'sandstone' | 'basalt' | 'canyon', D4AssetRecord>;

const CORAL = { file: 'tide-coral-mask-512.png', rgba8MipBytes: 1_398_100, colorSpace: 'none' } as const satisfies D4AssetRecord;

export const D4_MOBILE_ENVIRONMENT_BYTES = 6_990_504;
export const D4_MOBILE_ENVIRONMENT_MIB = 6.667;

export function shouldUseD4MobileTier(capabilities: D4AssetCapabilities): boolean {
  const shortLandscape = Boolean(capabilities.coarsePointer) && capabilities.cssHeight <= 520 && capabilities.cssWidth / Math.max(1, capabilities.cssHeight) > 1.5;
  return capabilities.cssWidth <= 430 || (capabilities.deviceMemory ?? Number.POSITIVE_INFINITY) <= 4 || shortLandscape;
}

/** Select exactly one tier before any TextureLoader is constructed or used. */
export function selectD4Assets(capabilities: D4AssetCapabilities): D4AssetSelection {
  const tier: D4AssetTier = shouldUseD4MobileTier(capabilities) ? 'mobile' : 'desktop';
  const environment = tier === 'mobile' ? MOBILE : DESKTOP;
  const requestedFiles = [environment.sandstone.file, environment.basalt.file, environment.canyon.file, CORAL.file] as const;
  return {
    tier,
    ...environment,
    coral: CORAL,
    requestedFiles,
    textureBytes: environment.sandstone.rgba8MipBytes + environment.basalt.rgba8MipBytes + environment.canyon.rgba8MipBytes + CORAL.rgba8MipBytes,
  };
}

// Keep the seven approved derivatives statically enumerable for Vite.  The
// selector above decides the tier before a loader exists, so the unused pair
// is bundled as a build artifact but never requested or uploaded at runtime.
const ASSET_URLS: Record<string, string> = {
  'tide-sandstone-base-1024.webp': new URL('../../assets/tide-scar-d4/tide-sandstone-base-1024.webp', import.meta.url).href,
  'tide-sandstone-base-mobile-512.webp': new URL('../../assets/tide-scar-d4/tide-sandstone-base-mobile-512.webp', import.meta.url).href,
  'tide-basalt-base-1024.webp': new URL('../../assets/tide-scar-d4/tide-basalt-base-1024.webp', import.meta.url).href,
  'tide-basalt-base-mobile-512.webp': new URL('../../assets/tide-scar-d4/tide-basalt-base-mobile-512.webp', import.meta.url).href,
  'tide-distant-canyon-2048x1024.webp': new URL('../../assets/tide-scar-d4/tide-distant-canyon-2048x1024.webp', import.meta.url).href,
  'tide-distant-canyon-mobile-1024x512.webp': new URL('../../assets/tide-scar-d4/tide-distant-canyon-mobile-1024x512.webp', import.meta.url).href,
  'tide-coral-mask-512.png': new URL('../../assets/tide-scar-d4/tide-coral-mask-512.png', import.meta.url).href,
};

function assetUrl(file: string): string {
  const url = ASSET_URLS[file];
  if (!url) throw new Error(`Unapproved D4 asset requested: ${file}`);
  return url;
}

function configureTexture(texture: Texture, record: D4AssetRecord): Texture {
  texture.colorSpace = record.colorSpace === 'srgb' ? SRGBColorSpace : NoColorSpace;
  texture.wrapS = texture.wrapT = RepeatWrapping;
  texture.needsUpdate = true;
  return texture;
}

function loaded(selection: D4AssetSelection, textures: D4LoadedAssets['textures'], fallback: boolean): D4LoadedAssets {
  let disposed = false;
  return {
    ...selection,
    textures,
    fallback,
    dispose: () => {
      if (disposed) return;
      disposed = true;
      if (!textures) return;
      Object.values(textures).forEach((texture) => texture.dispose());
    },
  };
}

/** Loading is best-effort presentation work: failure preserves flat PBR gameplay. */
export async function loadD4Assets(
  capabilities: D4AssetCapabilities,
  createLoader: () => D4TextureLoader = () => new TextureLoader(),
): Promise<D4LoadedAssets> {
  const selection = selectD4Assets(capabilities);
  const loader = createLoader();
  try {
    const [sandstone, basalt, canyon, coral] = await Promise.all([
      loader.loadAsync(assetUrl(selection.sandstone.file)),
      loader.loadAsync(assetUrl(selection.basalt.file)),
      loader.loadAsync(assetUrl(selection.canyon.file)),
      loader.loadAsync(assetUrl(selection.coral.file)),
    ]);
    return loaded(selection, {
      sandstone: configureTexture(sandstone, selection.sandstone),
      basalt: configureTexture(basalt, selection.basalt),
      canyon: configureTexture(canyon, selection.canyon),
      coral: configureTexture(coral, selection.coral),
    }, false);
  } catch {
    return loaded(selection, null, true);
  }
}
