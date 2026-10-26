// Container-only trusted timeout/descendant control; never a pilot implementation.
import { spawn } from 'node:child_process';
const child = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], { detached: true, stdio: 'ignore' });
child.unref();
console.log('Trusted lifecycle control: parent and detached descendant started');
while (true) { /* Deliberate CPU-bound hang; the whole container must be removed. */ }
