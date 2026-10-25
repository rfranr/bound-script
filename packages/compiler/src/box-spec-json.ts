import type { Postcondition, PrimitiveType, ValueType } from '@boundscript/artifact';

import type { BoxDevelopmentSpec, BoxSpecResult } from './box-development-spec.js';
import type { CompilationDiagnostic } from './index.js';

/** Invalid portable specification data; serialization never silently discards properties. */
export class BoxSpecValidationError extends Error {
  constructor(readonly diagnostics: readonly CompilationDiagnostic[]) {
    super(diagnostics.map((diagnostic) => diagnostic.message).join('\n'));
    this.name = 'BoxSpecValidationError';
  }
}

/** Canonical JSON: fixed keys, code-point-sorted record fields, two-space indent, one final LF. */
export function serializeBoxDevelopmentSpec(spec: BoxDevelopmentSpec): string {
  return `${JSON.stringify(normalizeSpec(spec), null, 2)}\n`;
}

/** Decode without source, parser services, bindings, filesystem access, or compilation. */
export function parseBoxDevelopmentSpec(json: string): BoxSpecResult {
  let value: unknown;
  try {
    value = JSON.parse(json);
  } catch {
    return { ok: false, diagnostics: [{
      code: 'compiler.box-spec.invalid-json', message: 'Box specification is not valid JSON.', severity: 'error'
    }] };
  }
  try {
    return { ok: true, spec: normalizeSpec(value), diagnostics: [] };
  } catch (error) {
    if (!(error instanceof BoxSpecValidationError)) throw error;
    return { ok: false, diagnostics: error.diagnostics };
  }
}

function invalid(path: string, message: string): never {
  throw new BoxSpecValidationError([{
    code: 'compiler.box-spec.invalid-spec', message: `${path}: ${message}`, severity: 'error'
  }]);
}

/** Inspect data properties before reading them; never invoke getters or toJSON hooks. */
function object(value: unknown, path: string, required: readonly string[], optional: readonly string[] = []): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value) ||
      (Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null)) {
    invalid(path, 'Expected a plain data object.');
  }
  const descriptors = Object.getOwnPropertyDescriptors(value);
  for (const key of Reflect.ownKeys(descriptors)) {
    if (typeof key !== 'string' || (!required.includes(key) && !optional.includes(key))) {
      invalid(path, `Unexpected property "${String(key)}".`);
    }
    const descriptor = descriptors[key]!;
    if (!Object.hasOwn(descriptor, 'value') || !descriptor.enumerable) {
      invalid(`${path}.${key}`, 'Expected an enumerable own data property.');
    }
  }
  for (const key of required) {
    if (!Object.hasOwn(descriptors, key)) invalid(`${path}.${key}`, 'Missing required property.');
  }
  return value as Record<string, unknown>;
}

function identifier(value: unknown, path: string): string {
  if (typeof value !== 'string' || !/^[A-Za-z_][A-Za-z0-9_]*$/.test(value)) {
    invalid(path, 'Expected an identifier.');
  }
  return value;
}

function primitive(value: unknown, path: string): PrimitiveType {
  if (value !== 'string' && value !== 'number' && value !== 'boolean') {
    invalid(path, 'Expected string, number, or boolean.');
  }
  return value;
}

function fieldsArray(value: unknown, path: string): readonly unknown[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) {
    invalid(path, 'Expected a plain array of fields.');
  }
  const keys = Reflect.ownKeys(value);
  if (keys.length !== value.length + 1) invalid(path, 'Sparse arrays and extra array properties are not supported.');
  for (let index = 0; index < value.length; index += 1) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(index));
    if (!descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable) {
      invalid(`${path}[${index}]`, 'Expected an enumerable own data element.');
    }
  }
  return value;
}

function valueType(value: unknown, path: string, records: Map<string, string>): ValueType {
  if (typeof value === 'string') return primitive(value, path);
  const record = object(value, path, ['kind', 'name', 'fields']);
  if (record.kind !== 'record') invalid(`${path}.kind`, 'Expected record.');
  const name = identifier(record.name, `${path}.name`);
  if (['string', 'number', 'boolean', 'void'].includes(name)) {
    invalid(`${path}.name`, 'Record name must not be a built-in type.');
  }
  const names = new Set<string>();
  const fields = fieldsArray(record.fields, `${path}.fields`).map((entry, index) => {
    const fieldPath = `${path}.fields[${index}]`;
    const field = object(entry, fieldPath, ['name', 'type']);
    const fieldName = identifier(field.name, `${fieldPath}.name`);
    if (names.has(fieldName)) invalid(`${fieldPath}.name`, `Duplicate record field "${fieldName}".`);
    names.add(fieldName);
    return { name: fieldName, type: primitive(field.type, `${fieldPath}.type`) };
  }).sort((left, right) => left.name < right.name ? -1 : left.name > right.name ? 1 : 0);
  const signature = JSON.stringify(fields);
  if (records.has(name) && records.get(name) !== signature) {
    invalid(path, `Conflicting schemas for record "${name}".`);
  }
  records.set(name, signature);
  return { kind: 'record', name, fields };
}

function postcondition(value: unknown, path: string, resultType: ValueType | 'void'): Postcondition {
  if (resultType === 'void') invalid(path, 'Void results cannot have a postcondition.');
  const predicate = object(value, path, ['kind', 'target', 'value']);
  if (predicate.kind !== 'string-not-equal') invalid(`${path}.kind`, 'Expected string-not-equal.');
  if (typeof predicate.value !== 'string') invalid(`${path}.value`, 'Expected a string literal value.');
  const target = object(predicate.target, `${path}.target`, ['kind'], ['name']);
  if (target.kind === 'result') {
    if (Object.hasOwn(target, 'name')) invalid(`${path}.target.name`, 'Unexpected property for a result target.');
    if (resultType !== 'string') invalid(`${path}.target`, 'Result target requires a string result.');
    return { kind: 'string-not-equal', target: { kind: 'result' }, value: predicate.value };
  }
  if (target.kind !== 'field') invalid(`${path}.target.kind`, 'Expected result or field.');
  const name = identifier(target.name, `${path}.target.name`);
  if (typeof resultType === 'string' || !resultType.fields.some((field) => field.name === name && field.type === 'string')) {
    invalid(`${path}.target.name`, 'Field target must name a declared string result field.');
  }
  return { kind: 'string-not-equal', target: { kind: 'field', name }, value: predicate.value };
}

/** Reconstruct only validated data in canonical order, never trusting an input object's JSON behavior. */
function normalizeSpec(value: unknown): BoxDevelopmentSpec {
  const spec = object(value, '$', ['format', 'version', 'system', 'box', 'operation']);
  if (spec.format !== 'boundscript/box-development-spec') invalid('$.format', 'Unsupported box specification format.');
  if (spec.version !== 1) invalid('$.version', 'Unsupported box specification version.');
  const system = identifier(spec.system, '$.system');
  const box = identifier(spec.box, '$.box');
  const operation = object(spec.operation, '$.operation', ['name', 'input', 'resultType'], ['postcondition']);
  const name = identifier(operation.name, '$.operation.name');
  const input = object(operation.input, '$.operation.input', ['name', 'type']);
  const inputName = identifier(input.name, '$.operation.input.name');
  const records = new Map<string, string>();
  const inputType = valueType(input.type, '$.operation.input.type', records);
  const resultType = operation.resultType === 'void' ? 'void' : valueType(operation.resultType, '$.operation.resultType', records);
  const predicate = Object.hasOwn(operation, 'postcondition')
    ? postcondition(operation.postcondition, '$.operation.postcondition', resultType) : undefined;
  return {
    format: 'boundscript/box-development-spec', version: 1, system, box,
    operation: {
      name, input: { name: inputName, type: inputType }, resultType,
      ...(predicate ? { postcondition: predicate } : {})
    }
  };
}
