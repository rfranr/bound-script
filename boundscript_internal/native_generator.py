"""Shared native generation; sandbox policy remains in agent_workspace/runtime."""
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback

from boundscript_internal.agent_workspace import agent_submission
from boundscript_internal.container_runtime import digest, runtime
from boundscript_internal.generation_diagnostics import report_generation_failure

PI = Path.home() / '.nvm/versions/node/v24.16.0/lib/node_modules/@earendil-works/pi-coding-agent'
AUTH = Path.home() / '.pi/agent/auth.json'
MODEL = 'openai-codex/gpt-5.6-luna'
MODEL_THINKING = 'low'
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')


def generation_prompt(box):
    return f'''Read /inputs/task.md and {box.contract_module} using the read tool.
Implement {box.function_type} in /implementation/implementation.ts and export the
{box.implementation_export} function. Use tools to write the file. Only the task and native
TypeScript contract are authorized inputs. No peer code, tests or repository are
available. Do not install packages, inspect or disclose credentials, or write
any other submission file. Use type-only relative imports from './contract'.
The contract and implementation stay siblings when integrated; never import sandbox paths.
Do not change the
contract or task. The container, not this prompt, enforces the filesystem boundary.
'''


def quarantine(submission, expected_digest, *, box_root):
    """Retain only the same bounded, credential-scanned bytes, never agent logs."""
    fd = os.open(submission, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise RuntimeError('Unsafe quarantine submission')
        source = stream.read(16385)
    if len(source) > 16384 or hashlib.sha256(source).hexdigest() != expected_digest:
        raise RuntimeError('Quarantine submission differs from credential-scanned source')
    directory = box_root / 'quarantine'
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError('Unsafe quarantine directory')
    saved = Path(tempfile.mkdtemp(prefix='failed-', dir=directory)) / 'implementation.ts'
    fd = os.open(saved, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(source)
    return saved


def generate(*, box_root, box, verification_command, detailed_diagnostics=False):
    """Generate and promote using an explicitly supplied independent verifier command."""
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    if detailed_diagnostics:
        print('Generation preflight: validating Box verification assets', flush=True)
    box.verification_files(box_root / box.verification_path)
    input_sources = {'task.md': box_root / box.task_path}
    contract = box_root / box.contract_path
    contract_digest = digest(contract)
    destination = box_root / box.accepted_path
    with agent_submission(runtime(), input_sources, pi=PI, auth=AUTH, box=box.name,
                          filename='implementation.ts', prompt=generation_prompt(box),
                          model=MODEL, thinking=MODEL_THINKING,
                          public_contract=contract) as (submission, scanned_digest):
        # Generation has ended; only source enters separate offline verification.
        verification = [*verification_command, '--box-definition', box.fingerprint(), str(submission)]
        if detailed_diagnostics:
            print('Generation: starting independent offline verification', flush=True)
        try:
            subprocess.run(verification, check=True, timeout=360)
        except (subprocess.SubprocessError, OSError):
            saved = quarantine(submission, scanned_digest, box_root=box_root)
            print(f'Verification failed; candidate quarantined: {saved.relative_to(box_root)}; '
                  f'sha256={scanned_digest}; not promoted', flush=True)
            raise
        assert digest(submission) == scanned_digest, 'Submission changed during verification'
        if detailed_diagnostics:
            print('Generation: promoting unchanged verified source', flush=True)
        assert digest(contract) == contract_digest, 'Public contract changed during generation/verification'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(submission, destination)
        assert digest(destination) == scanned_digest, 'Promoted source differs from verified bytes'
        print(f'PASS {box.name} independently verified and promoted unchanged; sha256={digest(destination)}', flush=True)


def cli(*, box_root, box, verification_command, detailed_diagnostics=False, args=()):
    if not __debug__:
        print('Generation stopped: Assertions must be enabled', file=sys.stderr)
        return 1
    try:
        if args:
            raise RuntimeError('This fixed Box runner expects no arguments')
        generate(box_root=box_root, box=box, verification_command=verification_command,
                 detailed_diagnostics=detailed_diagnostics)
    except Exception as error:
        if DEBUG:
            traceback.print_exc()
        if detailed_diagnostics:
            report_generation_failure(error)
        else:
            print(f'Generation stopped: {type(error).__name__}; no raw diagnostics emitted', file=sys.stderr)
        return 1
    return 0
