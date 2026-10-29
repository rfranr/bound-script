"""Bounded native source staging only; no execution, promotion or credentials."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

MAX_FILES = 16
MAX_BYTES = 16384
MAX_DEPTH = 8
MAX_PATH = 240
# Nonempty source trees need at most eight ancestor directories per source file.
MAX_ENTRIES = MAX_FILES * (MAX_DEPTH + 1)


def _open_directory(path):
    """Open each ancestor without following symlinks, then retain its descriptor."""
    path = Path(path)
    fd = os.open('/' if path.is_absolute() else '.', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:] if path.is_absolute() else path.parts:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def inventory_digest(records):
    """Digest trusted inventory records using the Node/Python scan encoding."""
    data = json.dumps(sorted(records), ensure_ascii=True, separators=(',', ':')).encode('ascii')
    return hashlib.sha256(data).hexdigest()


def _read_file(directory_fd, name, info, limit):
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Expected single-link regular TypeScript source files')
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
    with os.fdopen(fd, 'rb') as stream:
        if _identity(os.fstat(stream.fileno())) != _identity(info):
            raise ValueError('Source file changed during staging')
        data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Source tree exceeds aggregate size limit')
        if _identity(os.fstat(stream.fileno())) != _identity(info):
            raise ValueError('Source file changed during staging')
    return data


def _inventory(root_fd, destination=None, *, protected_contract=None):
    records, names = [], set()
    total = entries = 0
    contract_seen = False
    device = os.fstat(root_fd).st_dev

    def walk(directory_fd, parents):
        nonlocal total, entries, contract_seen
        before = _identity(os.fstat(directory_fd))
        with os.scandir(directory_fd) as children:
            for child in children:
                relative = '/'.join((*parents, child.name))
                if not (relative == 'contract.ts' and protected_contract is not None):
                    entries += 1
                if entries > MAX_ENTRIES:
                    raise ValueError('Source tree has too many entries')
                if (not re.fullmatch(r'[A-Za-z0-9_.-]+', child.name)
                        or child.name.casefold() in ('.', '..', 'node_modules', '.git')
                        or len(relative) > MAX_PATH or relative.casefold() in names):
                    raise ValueError('Unsafe or ambiguous source path')
                names.add(relative.casefold())
                info = os.stat(child.name, dir_fd=directory_fd, follow_symlinks=False)
                if info.st_dev != device:
                    raise ValueError('Source tree crosses a filesystem boundary')
                if relative.casefold() == 'contract.ts':
                    if relative != 'contract.ts' or protected_contract is None:
                        raise ValueError('Source tree collides with the consumer contract')
                    expected_info, expected_sha = protected_contract
                    if _identity(info) != _identity(expected_info):
                        raise ValueError('Protected contract changed during staging')
                    data = _read_file(directory_fd, child.name, info, expected_info.st_size)
                    if hashlib.sha256(data).hexdigest() != expected_sha:
                        raise ValueError('Protected contract changed during staging')
                    contract_seen = True
                    continue
                if stat.S_ISDIR(info.st_mode):
                    if len(parents) + 1 > MAX_DEPTH:
                        raise ValueError('Source tree exceeds directory depth limit')
                    fd = os.open(child.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                 dir_fd=directory_fd)
                    try:
                        if _identity(os.fstat(fd)) != _identity(info):
                            raise ValueError('Source directory changed during staging')
                        walk(fd, (*parents, child.name))
                    finally:
                        os.close(fd)
                else:
                    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                            or not child.name.endswith('.ts') or child.name.endswith('.d.ts')):
                        raise ValueError('Expected single-link regular TypeScript source files')
                    if len(records) >= MAX_FILES:
                        raise ValueError('Source tree exceeds file count limit')
                    data = _read_file(directory_fd, child.name, info, MAX_BYTES - total)
                    try:
                        data.decode('utf-8-sig')
                    except UnicodeError:
                        raise ValueError('Expected UTF-8 TypeScript source') from None
                    total += len(data)
                    records.append((relative, len(data), hashlib.sha256(data).hexdigest()))
                    if destination is not None:
                        target = destination / relative
                        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                        with target.open('xb') as output:
                            os.fchmod(output.fileno(), 0o600)
                            output.write(data)
        if _identity(os.fstat(directory_fd)) != before:
            raise ValueError('Source directory changed during staging')

    walk(root_fd, ())
    if protected_contract is not None and not contract_seen:
        raise ValueError('Protected contract is missing')
    if not any(path == 'implementation.ts' for path, _, _ in records):
        raise ValueError('Source tree requires public implementation.ts entry')
    return tuple(sorted(records))


@contextmanager
def staged_source_tree(submission, *, protected_contract=None):
    """Yield a private snapshot and in-memory inventory; always discard on exit.

    This is staging, not verification. Concurrent producer changes detected while
    copying fail closed; the snapshot does not claim atomic capture of a live tree.
    Only generation may supply (pre-writer stat, sha256) for its exact trusted
    contract.ts input; validate and omit it, never a generic ignore pattern.
    """
    with tempfile.TemporaryDirectory(prefix='boundscript-source-stage-') as tmp:
        snapshot = Path(tmp) / 'source'
        snapshot.mkdir(mode=0o700)
        try:
            root_fd = _open_directory(submission)
            try:
                options = {} if protected_contract is None else {'protected_contract': protected_contract}
                expected = _inventory(root_fd, snapshot, **options)
                if _inventory(root_fd, **options) != expected:
                    raise ValueError('Source tree changed during staging')
                reopened = _open_directory(submission)
                try:
                    if _identity(os.fstat(reopened)) != _identity(os.fstat(root_fd)):
                        raise ValueError('Source root changed during staging')
                finally:
                    os.close(reopened)
                snapshot_fd = _open_directory(snapshot)
                try:
                    if _inventory(snapshot_fd) != expected:
                        raise ValueError('Staged source differs from submitted bytes')
                finally:
                    os.close(snapshot_fd)
            finally:
                os.close(root_fd)
        except OSError:
            raise ValueError('Unsafe or unreadable source tree') from None
        yield snapshot, expected
