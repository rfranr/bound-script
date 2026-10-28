"""Developer traces without exception text, locals, source lines or agent events."""
from pathlib import Path
import sys
import traceback

from .container_runtime import ROOT, ResourcePolicyError


def report_generation_failure(error):
    print(f'Generation stopped: {type(error).__name__}; raw diagnostics withheld', file=sys.stderr)
    if type(error) is ResourcePolicyError:
        # Only this host-owned exception contains a deliberately safe diagnosis.
        print(f'Resource policy: {error}', file=sys.stderr)
    for frame, line in traceback.walk_tb(error.__traceback__):
        path = Path(frame.f_code.co_filename).resolve()
        try:
            relative = path.relative_to(ROOT)
        except ValueError:
            continue
        if relative.parts[0] not in ('boundscript_internal', 'experiments'):
            continue
        print(f'  at {relative.as_posix()}:{line} ({frame.f_code.co_name})', file=sys.stderr)
    print('No exception payloads, command output, credentials or agent events emitted.', file=sys.stderr)
