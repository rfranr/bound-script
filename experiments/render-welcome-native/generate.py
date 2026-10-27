#!/usr/bin/env python3
"""Fixed RenderWelcome generation, independent verification and local promotion."""
import hashlib
from importlib import import_module
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
sys.path.insert(0, str(SPIKE.parents[1]))
from boundscript_internal.agent_workspace import agent_submission
from boundscript_internal.container_runtime import digest, runtime
BOX = import_module('experiments.render-welcome-native.native_box').BOX

PI = Path.home() / '.nvm/versions/node/v24.16.0/lib/node_modules/@earendil-works/pi-coding-agent'
AUTH = Path.home() / '.pi/agent/auth.json'
MODEL = 'openai-codex/gpt-5.6-luna'
MODEL_THINKING = 'low'


def generation_prompt(box):
    return f'''Read /inputs/task.md and {box.contract_module} using the read tool.
Implement {box.function_type} in /implementation/implementation.ts and export the
{box.implementation_export} function. Use tools to write the file. Only the task and native
TypeScript contract are authorized inputs. No peer code, tests or repository are
available. Do not install packages, inspect or disclose credentials, or write
any other submission file. Use type-only contract imports. Do not change the
contract or task. The container, not this prompt, enforces the filesystem boundary.
'''


def quarantine(submission, expected_digest):
    """Retain only the same bounded, credential-scanned bytes, never agent logs."""
    fd = os.open(submission, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise RuntimeError('Unsafe quarantine submission')
        source = stream.read(16385)
    if len(source) > 16384 or hashlib.sha256(source).hexdigest() != expected_digest:
        raise RuntimeError('Quarantine submission differs from credential-scanned source')
    directory = SPIKE / 'quarantine'
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError('Unsafe quarantine directory')
    saved = Path(tempfile.mkdtemp(prefix='failed-', dir=directory)) / 'implementation.ts'
    fd = os.open(saved, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(source)
    return saved


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    if sys.argv[1:]:
        raise RuntimeError('This fixed Box runner expects no arguments')
    BOX.verification_files(SPIKE / BOX.verification_path)
    input_sources = {'task.md': SPIKE / BOX.task_path,
                     BOX.contract_module.removeprefix('/inputs/'): SPIKE / BOX.contract_path}
    destination = SPIKE / BOX.accepted_path
    with agent_submission(runtime(), input_sources, pi=PI, auth=AUTH, box=BOX.name,
                          filename='implementation.ts', prompt=generation_prompt(BOX),
                          model=MODEL, thinking=MODEL_THINKING) as (submission, scanned_digest):
        # Generation has ended; only the source enters independent offline verification.
        verification = [sys.executable, str(SPIKE / 'verify.py'),
                        '--box-definition', BOX.fingerprint(), str(submission)]
        try:
            subprocess.run(verification, check=True, timeout=360)
        except (subprocess.SubprocessError, OSError):
            saved = quarantine(submission, scanned_digest)
            print(f'Verification failed; candidate quarantined: {saved.relative_to(SPIKE)}; '
                  f'sha256={scanned_digest}; not promoted', flush=True)
            raise
        assert digest(submission) == scanned_digest, 'Submission changed during verification'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(submission, destination)
        print(f'PASS {BOX.name} independently verified and promoted unchanged; sha256={digest(destination)}', flush=True)


def cli():
    if not __debug__:
        print('Generation stopped: Assertions must be enabled', file=sys.stderr)
        return 1
    try:
        main()
    except Exception as error:
        # Never serialize arbitrary provider/tool diagnostics.
        print(f'Generation stopped: {type(error).__name__}; no raw diagnostics emitted', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(cli())
