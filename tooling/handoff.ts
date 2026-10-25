import { lstat, readFile, realpath, mkdir, mkdtemp, rename, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';

import { extractBoxDevelopmentSpec } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend } from '@boundscript/language';

import { renderPackage } from './handoff-render.js';

interface Selection { system: string; box: string; task: string; scope: string }
interface Binding { architecture: string; policy: string; boxes: Selection[] }
function fail(stage: string, context: string, message: string): never {
  throw new Error(`${stage} [${context}]: ${message}`);
}
function object(value: unknown, keys: string[], context: string): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('binding', context, 'Expected object');
  const obj = value as Record<string, unknown>;
  if (Object.keys(obj).length !== keys.length || keys.some((key) => !Object.hasOwn(obj, key))) {
    fail('binding', context, `Expected exactly ${keys.join(', ')}`);
  }
  return obj;
}
function relative(value: unknown): string {
  if (typeof value !== 'string' || !value || value.includes('\\') || value.includes('\0') ||
      value.includes(':') || value.split('/').some((part) => !part || part === '.' || part === '..')) {
    fail('path', String(value), 'Expected repository-relative POSIX path without traversal');
  }
  return value;
}
function identity(value: unknown, context: string): string {
  if (typeof value !== 'string' || !/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(value)) fail('binding', context, 'Invalid identity');
  return value;
}
function binding(value: unknown): Binding {
  const obj = object(value, ['format', 'version', 'architecture', 'policy', 'boxes'], 'input');
  if (obj.format !== 'boundscript/handoff-input' || obj.version !== 1) fail('binding', 'input', 'Unsupported format/version');
  if (!Array.isArray(obj.boxes) || !obj.boxes.length) fail('binding', 'boxes', 'Expected nonempty array');
  const seen = new Set<string>();
  const boxes = obj.boxes.map((value, i) => {
    const entry = object(value, ['system', 'box', 'task', 'scope'], `boxes[${i}]`);
    const system = identity(entry.system, `boxes[${i}].system`);
    const box = identity(entry.box, `boxes[${i}].box`);
    const key = `${system}/${box}`;
    if (seen.has(key)) fail('binding', key, 'Duplicate selection');
    seen.add(key);
    return { system, box, task: relative(entry.task), scope: relative(entry.scope) };
  });
  boxes.sort((a, b) => a.system < b.system ? -1 : a.system > b.system ? 1 : a.box < b.box ? -1 : a.box > b.box ? 1 : 0);
  return { architecture: relative(obj.architecture), policy: relative(obj.policy), boxes };
}
async function safeFile(root: string, relativePath: string): Promise<Buffer> {
  relative(relativePath);
  let current = root;
  const parts = relativePath.split('/');
  for (let i = 0; i < parts.length; i++) {
    current = path.join(current, parts[i]!);
    let stat;
    try { stat = await lstat(current); } catch { fail('input', relativePath, 'Missing/unreadable path'); }
    if (stat.isSymbolicLink() || (i === parts.length - 1 ? !stat.isFile() : !stat.isDirectory())) {
      fail('input', relativePath, 'Symlinks and nonregular files are forbidden');
    }
  }
  return readFile(current);
}
function utf8(bytes: Uint8Array, context: string): string {
  try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
  catch { fail('input', context, 'Invalid UTF-8'); }
}
async function markdown(root: string, file: string): Promise<Buffer> {
  const bytes = await safeFile(root, file);
  if (!utf8(bytes, file).trim()) fail('input', file, 'Empty Markdown');
  return bytes;
}
async function absent(destination: string): Promise<void> {
  try { await lstat(destination); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return; throw error; }
  fail('publication', destination, 'Destination already exists; use a fresh output');
}
/** Trusted local inputs; no candidate loading, authorization, or persistent execution state. */
export async function deriveHandoffs(options: {
  root: string; binding: string; output: string; selection: 'all' | { system: string; box: string };
}): Promise<void> {
  let stage = 'input';
  let context = options.binding;
  let staging: string | undefined;
  try {
    const root = await realpath(options.root);
    const output = path.resolve(options.output);
    await absent(output);
    const document = binding(JSON.parse(utf8(await safeFile(root, options.binding), options.binding)));
    const selection = options.selection;
    const selected = selection === 'all' ? document.boxes : document.boxes.filter((b) => b.system === selection.system && b.box === selection.box);
    if (!selected.length) fail('selection', JSON.stringify(selection), 'Unknown explicit selection');
    context = document.architecture;
    const source = utf8(await safeFile(root, document.architecture), document.architecture);
    stage = 'source';
    const parsed = await new BoundScriptLanguageFrontend().parse({ uri: document.architecture, text: source });
    if (!parsed.program || parsed.diagnostics.some((d) => d.severity === 'error')) {
      fail(stage, context, parsed.diagnostics.map((d) => d.message).join('; '));
    }
    const policy = await markdown(root, document.policy);
    const packages: { system: string; box: string; files: Record<string, Uint8Array> }[] = [];
    for (const selectedBox of selected) {
      context = `${selectedBox.system}/${selectedBox.box}`;
      stage = 'extraction';
      if (parsed.program.name !== selectedBox.system) fail(stage, context, 'System identity mismatch');
      const result = extractBoxDevelopmentSpec(parsed.program, selectedBox.box);
      if (!result.ok) fail(stage, context, result.diagnostics.map((d) => d.message).join('; '));
      stage = 'render';
      packages.push({ ...selectedBox, files: renderPackage(result.spec, {
        architecture: document.architecture, task: selectedBox.task, scope: selectedBox.scope, policy: document.policy
      }, { task: await markdown(root, selectedBox.task), scope: await markdown(root, selectedBox.scope), policy }) });
    }
    stage = 'publication';
    context = output;
    // Only the output parent is prepared. Every package is validated before staging.
    await mkdir(path.dirname(output), { recursive: true });
    staging = await mkdtemp(path.join(path.dirname(output), '.handoff-stage-'));
    for (const pkg of packages) {
      for (const [file, bytes] of Object.entries(pkg.files)) {
        const destination = path.join(staging, pkg.system, pkg.box, file);
        await mkdir(path.dirname(destination), { recursive: true });
        await writeFile(destination, bytes, { flag: 'wx' });
      }
    }
    await absent(output);
    await rename(staging, output);
    staging = undefined;
  } catch (error) {
    throw new Error(`${stage} [${context}]: ${error instanceof Error ? error.message : String(error)}`);
  } finally {
    if (staging) await rm(staging, { recursive: true, force: true });
  }
}
