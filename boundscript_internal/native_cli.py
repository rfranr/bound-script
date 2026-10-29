"""Shared verification entry point; selection belongs to the caller."""
from pathlib import Path

from boundscript_internal.native_verifier import check, VerificationFailure, quoted


def verify(args, *, box_root, box, baseline_source=None):
    if args[:1] == ['--box-definition']:
        if len(args) < 2 or args[1] != box.fingerprint():
            raise VerificationFailure('infrastructure', 'Generation/verification Box definition mismatch')
        args = args[2:]
    if args == ['--baseline'] and baseline_source is not None:
        submission = (box_root / baseline_source).resolve()
    elif len(args) <= 1 and (not args or not args[0].startswith('--')):
        submission = Path(args[0]).absolute() if args else box_root / box.accepted_path
    else:
        suffix = ' or --baseline' if baseline_source is not None else ''
        raise VerificationFailure('infrastructure', 'Expected optional candidate path' + suffix)
    try:
        check(submission, box_root=box_root, box=box)
    except Exception:
        print('Candidate retained in place (not promoted): ' + quoted(str(submission)), flush=True)
        raise


def cli(args, *, box_root, box, baseline_source=None):
    try:
        verify(args, box_root=box_root, box=box, baseline_source=baseline_source)
    except VerificationFailure as error:
        print(f'FAIL [{error.kind}] {error}', flush=True)
        return 1
    except Exception:
        print('FAIL [infrastructure] Verifier failed; raw diagnostics withheld', flush=True)
        return 1
    return 0
