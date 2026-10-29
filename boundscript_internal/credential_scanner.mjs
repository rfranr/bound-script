// Trusted scanner, sent over stdin by the workspace; never imports candidate code.
// Arguments contain only host policy, paths and a protected input hash, not secrets.
import fs from 'node:fs';
import { createHash } from 'node:crypto';

const C = fs.constants;
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const identity = info => ['dev', 'ino', 'mode', 'nlink', 'size', 'mtimeNs', 'ctimeNs'].map(k => info[k]);
const same = (a, b) => identity(a).every((value, i) => value === identity(b)[i]);
const fail = () => { throw new Error('Rejected source tree'); };

function openDirectory(path) {
  if (!path.startsWith('/')) fail();
  let fd = fs.openSync('/', C.O_RDONLY | C.O_DIRECTORY);
  try {
    for (const part of path.split('/').filter(Boolean)) {
      if (part === '.' || part === '..') fail();
      const next = fs.openSync(`/proc/self/fd/${fd}/${part}`, C.O_RDONLY | C.O_DIRECTORY | C.O_NOFOLLOW);
      fs.closeSync(fd);
      fd = next;
    }
    return fd;
  } catch (error) {
    fs.closeSync(fd);
    throw error;
  }
}

function readFile(parent, name, info, limit) {
  if (!info.isFile() || info.nlink !== 1n || info.size > BigInt(limit)) fail();
  const fd = fs.openSync(`/proc/self/fd/${parent}/${name}`, C.O_RDONLY | C.O_NOFOLLOW | C.O_NONBLOCK);
  try {
    if (!same(info, fs.fstatSync(fd, {bigint: true}))) fail();
    const bytes = Buffer.alloc(limit + 1);
    let length = 0;
    while (length < bytes.length) {
      const n = fs.readSync(fd, bytes, length, bytes.length - length, null);
      if (!n) break;
      length += n;
    }
    if (length > limit || !same(info, fs.fstatSync(fd, {bigint: true}))) fail();
    return bytes.subarray(0, length);
  } finally {
    fs.closeSync(fd);
  }
}

try {
  const config = JSON.parse(process.argv[2]);
  const secrets = [];
  function collect(value) {
    if (typeof value === 'string' && value.length >= 8) secrets.push(Buffer.from(value, 'utf8'));
    if (value && typeof value === 'object') for (const nested of Object.values(value)) collect(nested);
  }
  for (const path of config.auth) collect(JSON.parse(fs.readFileSync(path, 'utf8')));
  function check(bytes) {
    if (secrets.some(secret => bytes.includes(secret))) process.exit(42);
  }
  const records = [], names = new Set();
  let total = 0, entries = 0, contractSeen = false;
  const root = openDirectory(config.root);
  try {
    const device = fs.fstatSync(root, {bigint: true}).dev;
    function walk(fd, parents) {
      const before = fs.fstatSync(fd, {bigint: true});
      const directory = fs.opendirSync(`/proc/self/fd/${fd}`, {bufferSize: 1});
      try {
        for (let child; (child = directory.readSync()) !== null;) {
          const relative = [...parents, child.name].join('/');
          if (!(relative === 'contract.ts' && config.contract)) entries++;
          if (entries > config.limits.entries || !/^[A-Za-z0-9_.-]+$/.test(child.name) ||
              ['.', '..', 'node_modules', '.git'].includes(child.name.toLowerCase()) ||
              relative.length > config.limits.path || names.has(relative.toLowerCase())) fail();
          names.add(relative.toLowerCase());
          const info = fs.lstatSync(`/proc/self/fd/${fd}/${child.name}`, {bigint: true});
          if (info.dev !== device) fail();
          if (relative.toLowerCase() === 'contract.ts') {
            if (relative !== 'contract.ts' || !config.contract) fail();
            const data = readFile(fd, child.name, info, config.contract.size);
            if (hash(data) !== config.contract.sha256) fail();
            contractSeen = true;
            continue;
          }
          check(Buffer.from(relative, 'ascii'));
          if (info.isDirectory()) {
            if (parents.length + 1 > config.limits.depth) fail();
            const nested = fs.openSync(`/proc/self/fd/${fd}/${child.name}`,
                                      C.O_RDONLY | C.O_DIRECTORY | C.O_NOFOLLOW);
            try {
              if (!same(info, fs.fstatSync(nested, {bigint: true}))) fail();
              walk(nested, [...parents, child.name]);
            } finally {
              fs.closeSync(nested);
            }
          } else {
            if (records.length >= config.limits.files || !child.name.endsWith('.ts') ||
                child.name.endsWith('.d.ts')) fail();
            const data = readFile(fd, child.name, info, config.limits.bytes - total);
            new TextDecoder('utf-8', {fatal: true}).decode(data);
            check(data);
            total += data.length;
            records.push([relative, data.length, hash(data)]);
          }
        }
      } finally {
        directory.closeSync();
      }
      if (!same(before, fs.fstatSync(fd, {bigint: true}))) fail();
    }
    walk(root, []);
    if ((config.contract && !contractSeen) || !records.some(record => record[0] === 'implementation.ts')) fail();
    const reopened = openDirectory(config.root);
    try {
      if (!same(fs.fstatSync(root, {bigint: true}), fs.fstatSync(reopened, {bigint: true}))) fail();
    } finally {
      fs.closeSync(reopened);
    }
    records.sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
    console.log(hash(Buffer.from(JSON.stringify(records), 'ascii')));
  } finally {
    fs.closeSync(root);
  }
} catch {
  // Even filesystem errors may contain secret-bearing filenames. Never print them.
  process.exit(43);
}
