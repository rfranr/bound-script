#!/usr/bin/env python3
"""Fixed NormalizeContact entry point for the shared offline verifier."""
from importlib import import_module
from pathlib import Path
import sys

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
sys.path.insert(0, str(SPIKE.parents[1]))
from boundscript_internal.native_verifier import check as verify_candidate, VerificationFailure, quoted
configuration = import_module('experiments.native-typescript-contracts.native_box')
BOX = configuration.BOX
BASELINE_SOURCE = configuration.BASELINE_SOURCE


def check(submission):
    verify_candidate(submission, box_root=SPIKE, box=BOX)


def main():
    args = sys.argv[1:]
    if args[:1] == ['--box-definition']:
        if len(args) < 2 or args[1] != BOX.fingerprint():
            raise VerificationFailure('infrastructure', 'Generation/verification Box definition mismatch')
        args = args[2:]
    if args == ['--baseline']:
        submission = (SPIKE / BASELINE_SOURCE).resolve()
    elif len(args) <= 1 and (not args or not args[0].startswith('--')):
        submission = Path(args[0]).absolute() if args else SPIKE / BOX.accepted_path
    else:
        raise VerificationFailure('infrastructure', 'Expected optional candidate path or --baseline')
    try:
        check(submission)
    except Exception:
        print('Candidate retained in place (not promoted): ' + quoted(str(submission)), flush=True)
        raise


def cli():
    try:
        main()
    except VerificationFailure as error:
        print(f'FAIL [{error.kind}] {error}', flush=True)
        return 1
    except Exception:
        print('FAIL [infrastructure] Verifier failed; raw diagnostics withheld', flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(cli())
