import type { Postcondition, ValueType } from '@boundscript/artifact';

/** Internal checks shared by director execution and standalone verification. */
export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isPrimitiveType(value: unknown): value is 'string' | 'number' | 'boolean' {
  return value === 'string' || value === 'number' || value === 'boolean';
}

export function isValueType(value: unknown): value is ValueType {
  if (isPrimitiveType(value)) return true;
  if (!isRecord(value) || value.kind !== 'record' || typeof value.name !== 'string' ||
      !value.name || !Array.isArray(value.fields)) return false;
  const names = new Set<string>();
  return value.fields.every((field) => {
    if (!isRecord(field) || typeof field.name !== 'string' || !field.name ||
        !isPrimitiveType(field.type) || names.has(field.name)) return false;
    names.add(field.name);
    return true;
  });
}

export function isPostcondition(value: unknown, resultType: ValueType): value is Postcondition {
  if (!isRecord(value) || value.kind !== 'string-not-equal' || typeof value.value !== 'string' ||
      !isRecord(value.target)) return false;
  const target = value.target;
  return (target.kind === 'result' && resultType === 'string') ||
    (target.kind === 'field' && typeof target.name === 'string' &&
      typeof resultType !== 'string' && resultType.fields.some(
        (field) => field.name === target.name && field.type === 'string'
      ));
}

export function valueCategory(value: unknown): string {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  if (typeof value === 'number' && !Number.isFinite(value)) return 'non-finite number';
  return typeof value;
}

export function valueTypeProblem(value: unknown, type: ValueType): string | undefined {
  if (typeof type === 'string') {
    return typeof value === type && (type !== 'number' || Number.isFinite(value))
      ? undefined : `got ${valueCategory(value)}`;
  }
  if (!isRecord(value) || Array.isArray(value)) return `expected record, got ${valueCategory(value)}`;
  const fields = new Set(type.fields.map((field) => field.name));
  for (const field of type.fields) {
    if (!Object.hasOwn(value, field.name)) return `missing required field "${field.name}"`;
    const problem = valueTypeProblem(value[field.name], field.type);
    if (problem) return `field "${field.name}" expected ${field.type}, ${problem}`;
  }
  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== 'string' || !fields.has(key)) return `unexpected field "${String(key)}"`;
  }
  return undefined;
}

export function resultTypeProblem(value: unknown, type: ValueType | 'void'): string | undefined {
  return type === 'void'
    ? (value === undefined ? undefined : `got ${valueCategory(value)}`)
    : valueTypeProblem(value, type);
}

/** Only after full output validation and descriptor compatibility checks. May read a getter. */
export function postconditionViolation(result: unknown, predicate: Postcondition): string | undefined {
  const observed = predicate.target.kind === 'result'
    ? result : (result as Record<string, unknown>)[predicate.target.name];
  return observed === predicate.value ? observed : undefined;
}
