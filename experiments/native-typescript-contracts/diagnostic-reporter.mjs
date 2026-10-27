import { writeFileSync } from 'node:fs';

// Offline verifier only. Never serialize console output, messages, stacks,
// environment, or arbitrary error properties. Host applies a second sanitization.
export function collectDiagnostics(modules, unhandledErrors) {
  const failed = [];
  let infrastructureErrors = unhandledErrors.length;
  for (const module of modules) {
    infrastructureErrors += module.errors().length;
    for (const test of module.children.allTests('failed')) {
      if (failed.length >= 10) break;
      const assertions = [];
      for (const original of test.result().errors ?? []) {
        // fast-check wraps the original assertion as its cause.
        let error = original;
        for (let depth = 0; error && depth < 4; depth++, error = error.cause) {
          if (error.name !== 'AssertionError' || assertions.length >= 2) continue;
          const fields = {};
          for (const key of ['expected', 'actual', 'diff']) {
            if (typeof error[key] === 'string') fields[key] = error[key].length <= 2000
              ? error[key] : '[oversized assertion value withheld]';
            else if (['number', 'boolean'].includes(typeof error[key]) || error[key] === null)
              fields[key] = error[key];
          }
          assertions.push(fields);
        }
      }
      failed.push({ file: module.moduleId.split('/').pop(),
        name: test.fullName.length <= 300 ? test.fullName : '[oversized test name withheld]', assertions });
    }
  }
  return { complete: true, infrastructureErrors, failed };
}

export default class DiagnosticReporter {
  onTestRunEnd(modules, unhandledErrors) {
    writeFileSync('/implementation/vitest-diagnostics.json',
      JSON.stringify(collectDiagnostics(modules, unhandledErrors)));
  }
}
