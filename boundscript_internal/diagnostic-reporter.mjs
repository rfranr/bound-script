import { writeFileSync } from 'node:fs';

const bounded = (value, limit) => typeof value === 'string' && value.length <= limit
  ? value : '[oversized or unavailable field withheld]';
const valueType = value => value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;

// A narrow adapter over Vitest's structured TestCase API, not a test runner.
// No console output, error messages/stacks, counterexamples or environment dumps.
export function collectDiagnostics(modules, unhandledErrors) {
  const tests = [];
  const files = [];
  const failed = [];
  let infrastructureErrors = unhandledErrors.length;
  for (const module of modules) {
    infrastructureErrors += module.errors().length;
    const file = module.moduleId.startsWith('/checks/') ? module.moduleId.slice('/checks/'.length)
      : '[outside checks]';
    if (files.length < 100) files.push(bounded(file, 300));
    else infrastructureErrors++;
    for (const test of module.children.allTests()) {
      const result = test.result();
      const item = { file: bounded(file, 300),
        name: bounded(test.fullName, 300), status: result.state };
      if (tests.length < 100) tests.push(item);
      else infrastructureErrors++; // Truncation must never turn omitted tests into success.
      if (result.state !== 'failed' || failed.length >= 10) continue;
      const assertions = [];
      const typia = [];
      let timedOut = false;
      for (const original of result.errors ?? []) {
        // fast-check wraps original assertion/Typia errors as causes.
        let error = original;
        for (let depth = 0; error && depth < 4; depth++, error = error.cause) {
          // Vitest exposes no dedicated timeout code; classify its fixed prefix
          // without exporting the message (which can contain candidate text).
          if (typeof error.message === 'string' && /^(Test|Hook) timed out in \d+ms/.test(error.message))
            timedOut = true;
          if (typeof error.method === 'string' && error.method.startsWith('typia.') && typia.length < 2) {
            typia.push({ path: bounded(error.path, 300), expected: bounded(error.expected, 500),
              actualType: valueType(error.value) });
          }
          if (error.name !== 'AssertionError' || assertions.length >= 2) continue;
          const fields = {};
          for (const key of ['expected', 'actual', 'diff']) {
            if (typeof error[key] === 'string') fields[key] = bounded(error[key], 2000);
            else if (['number', 'boolean'].includes(typeof error[key]) || error[key] === null)
              fields[key] = error[key];
          }
          assertions.push(fields);
        }
      }
      failed.push({ ...item, assertions, typia, timedOut });
    }
  }
  return { complete: true, infrastructureErrors, files, tests, failed };
}

export default class DiagnosticReporter {
  onTestRunEnd(modules, unhandledErrors) {
    writeFileSync('/implementation/vitest-diagnostics.json',
      JSON.stringify(collectDiagnostics(modules, unhandledErrors)));
  }
}
