#!/usr/bin/env node

import { runBoundCli } from './index.js';

process.exitCode = await runBoundCli(process.argv.slice(2), {
  stdout: process.stdout,
  stderr: process.stderr
});
