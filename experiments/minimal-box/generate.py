#!/usr/bin/env python3
"""Fixed Greeting/0018 Pi runs; no generic runner or user-defined job format."""
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from boundscript_internal.agent_workspace import agent_submission
from boundscript_internal.container_runtime import digest, runtime

HERE = Path(__file__).resolve().parent
PI = Path.home() / '.nvm/versions/node/v24.16.0/lib/node_modules/@earendil-works/pi-coding-agent'
AUTH = Path.home() / '.pi/agent/auth.json'
MODEL = 'openai-codex/gpt-6.1-sol'
PROMPT = '''Read /inputs/task.md, /inputs/contract.ts and /inputs/slugger.ts using tools.
Implement the existing Greeting Box in /implementation/greet.ts. Use the tools to
write the file, not just describe it. No acceptance tests or peer code are available.
Network and authentication are provisioned as runtime capabilities per the task.
Do not inspect, print, copy into the submission, or transmit credential files or
runtime state.
Do not install packages. Keep your only submission file greet.ts. Do not alter the
contract or task. The filesystem boundary is enforced by the container runtime, not this prompt.
'''


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    if sys.argv[1:] == ['--pair']:
        # Two fresh processes/containers, not a shared agent session or context.
        for box in ('normalize-contact', 'render-welcome'):
            subprocess.run([sys.executable, __file__, box], check=True, timeout=450)
        subprocess.run([sys.executable, str(HERE / 'verify_pair.py'), 'integrate'], check=True, timeout=120)
        return
    if sys.argv[1:] not in ([], ['normalize-contact'], ['render-welcome']):
        raise RuntimeError('Expected no args, --pair, normalize-contact, or render-welcome')
    box = sys.argv[1] if len(sys.argv) == 2 else 'greeting'
    filename = 'greet.ts' if box == 'greeting' else 'implementation.ts'
    input_sources = {'task.md': HERE / 'task.md', 'contract.ts': HERE / 'contract.ts',
                     'slugger.ts': HERE / 'slugger.ts'}
    destination = HERE / 'implementation/greet.ts'
    prompt = PROMPT
    if box != 'greeting':
        pair = HERE / 'two-boxes'
        input_sources = {'task.md': pair / f'tasks/{box}.md', 'contract.ts': pair / f'contracts/{box}.ts'}
        if box == 'render-welcome':
            input_sources['normalize-contact.ts'] = pair / 'contracts/normalize-contact.ts'
        destination = pair / f'accepted/{box}.ts'
        prompt = ('Use the read tool to inspect these authorized inputs: '
                  + ', '.join('/inputs/' + name for name in input_sources)
                  + '. Implement the task in /implementation/implementation.ts using tools. '
                    'Export the exact named function required by the task. No tests, application '
                    'wiring or peer implementations are available. Do not install packages, '
                    'inspect or disclose credentials, or write any other submission file. '
                    'Do not change contracts or business requirements.')
    with agent_submission(runtime(), input_sources, pi=PI, auth=AUTH, box=box,
                          filename=filename, prompt=prompt, model=MODEL, thinking='medium') as (submission, scanned_digest):
        verification = ([sys.executable, str(HERE / 'verify.py'), str(submission)] if box == 'greeting'
                        else [sys.executable, str(HERE / 'verify_pair.py'), box, str(submission)])
        subprocess.run(verification, check=True, timeout=120)
        assert digest(submission) == scanned_digest, 'Submission changed during verification'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(submission, destination)
        print(f'PASS {box} independently verified and promoted unchanged; sha256={digest(destination)}', flush=True)


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
