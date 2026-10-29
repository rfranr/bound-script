"""Explicit local promotion only; never generation or automatic acceptance."""
import argparse
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile

from boundscript_internal import native_verifier, source_tree as tree


def read_bytes(path, limit=8 * 1024 * 1024):
    fd = tree._open_directory(path.parent)
    try:
        info = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        return tree._read_file(fd, path.name, info, limit)
    finally:
        os.close(fd)


def inputs(root, box):
    files = [box.contract_path, box.task_path]
    files += [str(Path(box.verification_path) / name)
              for name in box.verification_files(root / box.verification_path)]
    if any(Path(name).is_absolute() or '..' in Path(name).parts for name in files):
        raise ValueError('Unsafe Box input path')
    return {name: read_bytes(root / name) for name in sorted(set(files))}


def candidate(root, box, identifier):
    directory = root / 'candidates' / identifier
    fd = tree._open_directory(directory)
    try:
        if set(os.listdir(fd)) != {'source', 'review.json'}:
            raise ValueError('Unexpected candidate contents')
    finally:
        os.close(fd)
    raw = read_bytes(directory / 'review.json', 16384)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate metadata key')
            result[key] = value
        return result
    review = json.loads(raw, object_pairs_hook=unique)
    required = {'box', 'candidate_id', 'source_inventory_digest', 'source_file_count',
                'verification_result', 'model', 'reasoning'}
    if (not isinstance(review, dict) or set(review) != required
            or review['box'] != box.name or review['candidate_id'] != identifier
            or review['verification_result'] != 'PASS'
            or type(review['source_file_count']) is not int
            or not isinstance(review['source_inventory_digest'], str)
            or not re.fullmatch('[0-9a-f]{64}', review['source_inventory_digest'])
            or any(not isinstance(review[key], str) or not review[key]
                   for key in ('model', 'reasoning'))):
        raise ValueError('Invalid candidate review')
    with tree.staged_source_tree(directory / 'source') as (_, records):
        if (tree.inventory_digest(records) != review['source_inventory_digest']
                or len(records) != review['source_file_count']):
            raise ValueError('Candidate inventory mismatch')
    return raw, records


def publish_noreplace(parent_fd, staging, version):
    # Linux no-replace directory rename: atomic publication, including against
    # writers that do not participate in our advisory sequence lock.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = libc.renameat2
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(parent_fd, staging.encode(), parent_fd, version.encode(), 1):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def promote(*, box_root, box, candidate_id):
    if not __debug__:
        raise ValueError('Assertions must be enabled')
    if not re.fullmatch('[0-9a-f]{32}', candidate_id):
        raise ValueError('Unsafe candidate ID')
    fingerprint = box.fingerprint()
    original, records = candidate(box_root, box, candidate_id)
    owned_inputs = inputs(box_root, box)
    with tempfile.TemporaryDirectory(prefix='boundscript-promotion-') as temporary:
        frozen = Path(temporary)
        for name, data in owned_inputs.items():
            target = frozen / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        with tree.staged_source_tree(box_root / 'candidates' / candidate_id / 'source') as (source, staged):
            if staged != records:
                raise ValueError('Candidate changed before verification')
            # The existing verifier receives only frozen, consumer-owned inputs.
            native_verifier.check(source, box_root=frozen, box=box, source_tree=True)

            def integrity():
                if (box.fingerprint() != fingerprint or inputs(box_root, box) != owned_inputs
                        or inputs(frozen, box) != owned_inputs
                        or candidate(box_root, box, candidate_id) != (original, records)):
                    raise ValueError('Promotion inputs changed')
                with tree.staged_source_tree(source) as (_, current):
                    if current != records:
                        raise ValueError('Verified source changed')

            integrity()
            versions = box_root / 'versions'
            versions.mkdir(mode=0o700, exist_ok=True)
            fd = tree._open_directory(versions)
            try:
                info = os.fstat(fd)
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                    raise ValueError('Versions directory must be private and host-owned')
                fcntl.flock(fd, fcntl.LOCK_EX)
                names = os.listdir(fd)
                if any(not re.fullmatch(r'[0-9]{4,}', name) for name in names):
                    raise ValueError('Unexpected versions entry; inspect interrupted publication')
                for name in names:
                    if not stat.S_ISDIR(os.stat(name, dir_fd=fd, follow_symlinks=False).st_mode):
                        raise ValueError('Unsafe version entry')
                version = f'{max((int(name) for name in names), default=0) + 1:04d}'
                anchored = Path(f'/proc/self/fd/{fd}')
                staging = Path(tempfile.mkdtemp(prefix='.pending-', dir=anchored))
                try:
                    shutil.copytree(source, staging / 'source')
                    copied_fd = os.open(staging / 'source', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                    try:
                        if tree._inventory(copied_fd) != records:
                            raise ValueError('Published copy differs')
                    finally:
                        os.close(copied_fd)
                    manifest = {'candidate_id': candidate_id, 'box': box.name, 'version': version,
                                'source_inventory_digest': tree.inventory_digest(records),
                                'box_definition_fingerprint': fingerprint,
                                'verification_inputs': {name: hashlib.sha256(data).hexdigest()
                                                        for name, data in owned_inputs.items()}}
                    (staging / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
                    integrity()
                    publish_noreplace(fd, staging.name, version)
                finally:
                    if staging.exists():
                        shutil.rmtree(staging)
            finally:
                os.close(fd)
    return version


def cli(args, *, box_root, box):
    parser = argparse.ArgumentParser(description='Explicitly authorize promotion of one verified candidate')
    parser.add_argument('--candidate', required=True)
    options = parser.parse_args(args)
    try:
        version = promote(box_root=box_root, box=box, candidate_id=options.candidate)
    except Exception as error:
        print(f'Promotion stopped: {type(error).__name__}; no version published', file=sys.stderr)
        return 1
    print(f'PASS {box.name}: published versions/{version}; candidate preserved')
    return 0
