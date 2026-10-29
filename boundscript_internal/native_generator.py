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

from boundscript_internal import source_tree as tree
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


def agent_owned_prompt(box):
    return f'''Read /inputs/task.md and {box.contract_module} using the read tool.
Implement {box.function_type}; the public entry is /implementation/implementation.ts
and its named function export is {box.implementation_export}. Preserve the public contract.
Use tools to write supported TypeScript sources within /implementation only.
Only the task and native TypeScript contract are authorized inputs. No peer code,
tests or repository are available. Do not install packages, inspect or disclose
credentials, or change the contract or task. Imports must be relative; imports of
contract types must be type-only. Never import sandbox paths.
Output must be regular UTF-8 .ts source, not .d.ts, dependency, configuration or
emitted files. Limits: {tree.MAX_FILES} source files, {tree.MAX_BYTES} total bytes,
depth {tree.MAX_DEPTH}, {tree.MAX_PATH}-byte ASCII relative paths, and
{tree.MAX_ENTRIES} traversed entries. Unsafe objects and path collisions are prohibited.
The container, not this prompt, enforces the filesystem boundary.
'''


def verify_agent_owned(submission, scanned_digest, *, verification_command, box,
                       protected):
    """Verify the entire private snapshot; never publish or retain its sources."""
    def inventory():
        with tree.staged_source_tree(submission) as (_, records):
            if tree.inventory_digest(records) != scanned_digest:
                raise RuntimeError('Complete source changed during verification handoff')
            return len(records)

    def integrity():
        if any(digest(path) != sha for path, sha in protected.items()):
            raise RuntimeError('Public generation inputs changed during verification')

    try:
        count = inventory()
        integrity()
        subprocess.run([*verification_command, '--box-definition', box.fingerprint(),
                        '--source-tree', str(submission)], check=True, timeout=360)
        inventory()
        integrity()
        print(f'PASS {box.name} independently verified temporary source tree; '
              f'files={count}; sha256={scanned_digest}; not promoted', flush=True)
    finally:
        print('Agent-owned output: temporary sources discarded on cleanup; '
              'no promotion or quarantine', flush=True)


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


def generate(*, box_root, box, verification_command, detailed_diagnostics=False,
             agent_owned=False):
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
    protected = {path: digest(path) for path in (contract, *input_sources.values())} if agent_owned else {}
    options = {'source_tree': True} if agent_owned else {}
    prompt = agent_owned_prompt(box) if agent_owned else generation_prompt(box)
    with agent_submission(runtime(), input_sources, pi=PI, auth=AUTH, box=box.name,
                          filename='implementation.ts', prompt=prompt,
                          model=MODEL, thinking=MODEL_THINKING,
                          public_contract=contract, **options) as (submission, scanned_digest):
        if agent_owned:
            verify_agent_owned(submission, scanned_digest,
                               verification_command=verification_command, box=box,
                               protected=protected)
            return
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
        if args and list(args) != ['--agent-owned']:
            raise RuntimeError('Expected no arguments or --agent-owned')
        options = {'agent_owned': True} if args else {}
        generate(box_root=box_root, box=box, verification_command=verification_command,
                 detailed_diagnostics=detailed_diagnostics, **options)
    except Exception as error:
        if DEBUG:
            traceback.print_exc()
        if detailed_diagnostics:
            report_generation_failure(error)
        else:
            print(f'Generation stopped: {type(error).__name__}; no raw diagnostics emitted', file=sys.stderr)
        return 1
    return 0
