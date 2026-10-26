// Compile-only bidirectional signature checks. Never executed.
import type { normalize, render } from './interfaces.js';
import type { Implementation as NormalizeImplementation } from './NormalizeContact/generated/contract.js';
import type { Implementation as RenderImplementation } from './RenderWelcome/generated/contract.js';
declare const normalizer: typeof normalize;
declare const renderer: typeof render;
const n: NormalizeImplementation = normalizer;
const r: RenderImplementation = renderer;
const backN: typeof normalize = n;
const backR: typeof render = r;
export type Checked = [typeof backN, typeof backR];
